"""Executable source contracts loaded from versioned YAML."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import pandas as pd
import pandera.pandas as pa
import yaml

from fieldforge.settings import ROOT

DEFAULT_CONTRACT_PATH = ROOT / "config" / "source_contracts.yml"


class SourceContractError(ValueError):
    """Raised when an extract does not match its declared structural boundary."""


def load_source_contracts(path: Path = DEFAULT_CONTRACT_PATH) -> dict[str, Any]:
    """Safely load and validate the source-contract registry itself."""
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise SourceContractError(f"Cannot load source contracts from {path}: {error}") from error
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise SourceContractError("Source contracts must be a version 1 mapping")
    sources = payload.get("sources")
    if not isinstance(sources, dict) or not sources:
        raise SourceContractError("Source contracts must declare a non-empty sources mapping")
    for source, contract in sources.items():
        if not isinstance(contract, dict):
            raise SourceContractError(f"Contract for {source} must be a mapping")
        columns = contract.get("columns")
        if not isinstance(columns, list) or not columns or not all(isinstance(x, str) for x in columns):
            raise SourceContractError(f"Contract for {source} must declare ordered string columns")
        if len(columns) != len(set(columns)):
            raise SourceContractError(f"Contract for {source} contains duplicate columns")
        keys = contract.get("primary_key")
        keys = [keys] if isinstance(keys, str) else keys
        if not isinstance(keys, list) or not keys or not set(keys).issubset(columns):
            raise SourceContractError(f"Contract for {source} has an invalid primary key")
    return payload


def validate_source_frame(
    source: str,
    frame: pd.DataFrame,
    contract_path: Path = DEFAULT_CONTRACT_PATH,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate one raw extract before any provenance columns or business rules are added."""
    contracts = load_source_contracts(contract_path)
    contract = contracts["sources"].get(source)
    if contract is None:
        raise SourceContractError(f"No source contract declared for {source}")
    columns = contract["columns"]
    schema = pa.DataFrameSchema(
        {column: pa.Column(str, nullable=False, coerce=True) for column in columns},
        strict=True,
        ordered=True,
        name=f"{source}_raw_extract",
    )
    try:
        validated = schema.validate(frame, lazy=True)
    except (pa.errors.SchemaError, pa.errors.SchemaErrors) as error:
        raise SourceContractError(f"{source} extract violates its structural contract: {error}") from error
    receipt = {
        "source": source,
        "rows": len(validated),
        "columns": columns,
        "primary_key": contract["primary_key"],
        "status": "passed",
        "engine": "Pandera",
        "registry_loader": "yaml.safe_load",
        "contract_sha256": hashlib.sha256(contract_path.read_bytes()).hexdigest(),
    }
    return validated, receipt
