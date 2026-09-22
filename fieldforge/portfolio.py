"""Executable checks for reviewer-facing evidence and repository knowledge."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import pandera.pandas as pa
import yaml

from fieldforge.settings import ROOT, artifacts_root
from fieldforge.utils import write_json

DEFAULT_INVENTORY = ROOT / "config" / "tool_inventory.yml"
EXPECTED_TOOL_IDS = set(range(1, 39))
REQUIRED_DOCS = (
    "README.md",
    "CLAUDE.md",
    "docs/architecture.md",
    "docs/acceptance-criteria.md",
    "docs/kpi-audit.md",
    "docs/repository-knowledge.md",
    "docs/resume-bullets.md",
    "docs/tools-and-evidence.md",
)
ACTIVE_DOCS = (
    "README.md",
    "CLAUDE.md",
    "docs/demo.md",
    "docs/tools-and-evidence.md",
    "docs/repository-knowledge.md",
)
FORBIDDEN_ACTIVE_TEXT = ("claudework", "0/38", "interview-practice-plan")


class PortfolioCheckError(ValueError):
    """Raised when the portfolio evidence contract is incomplete."""


def load_tool_inventory(path: Path = DEFAULT_INVENTORY) -> list[dict[str, Any]]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        raise PortfolioCheckError(f"Cannot load tool inventory: {error}") from error
    if not isinstance(payload, dict) or payload.get("version") != 1:
        raise PortfolioCheckError("Tool inventory must be a version 1 mapping")
    tools = payload.get("tools")
    if not isinstance(tools, list):
        raise PortfolioCheckError("Tool inventory must contain a tools list")
    frame = pd.DataFrame(
        {
            "id": [tool.get("id") for tool in tools],
            "name": [tool.get("name") for tool in tools],
            "usage": [tool.get("usage") for tool in tools],
            "evidence_count": [len(tool.get("evidence", [])) for tool in tools],
        }
    )
    schema = pa.DataFrameSchema(
        {
            "id": pa.Column(int, unique=True, checks=pa.Check.isin(EXPECTED_TOOL_IDS)),
            "name": pa.Column(str, unique=True, checks=pa.Check.str_length(min_value=2)),
            "usage": pa.Column(str, checks=pa.Check.str_length(min_value=10)),
            "evidence_count": pa.Column(int, checks=pa.Check.ge(1)),
        },
        strict=True,
    )
    try:
        schema.validate(frame, lazy=True)
    except (pa.errors.SchemaError, pa.errors.SchemaErrors) as error:
        raise PortfolioCheckError(f"Tool inventory schema failed: {error}") from error
    if set(frame["id"]) != EXPECTED_TOOL_IDS:
        raise PortfolioCheckError("Tool inventory must contain exactly IDs 1 through 38")
    return tools


def portfolio_check(
    root: Path = ROOT,
    inventory_path: Path = DEFAULT_INVENTORY,
    write_receipt: bool = True,
) -> dict[str, Any]:
    tools = load_tool_inventory(inventory_path)
    missing_evidence = sorted(
        {path for tool in tools for path in tool["evidence"] if not (root / path).exists()}
    )
    missing_docs = [path for path in REQUIRED_DOCS if not (root / path).is_file()]
    stale_references = []
    for relative in ACTIVE_DOCS:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8").lower()
        stale_references.extend(
            f"{relative}: {term}" for term in FORBIDDEN_ACTIVE_TEXT if term in text
        )
    payload = {
        "checked_at_utc": datetime.now(UTC).isoformat(),
        "status": "passed" if not (missing_evidence or missing_docs or stale_references) else "failed",
        "tool_count": len(tools),
        "tool_ids_complete": {tool["id"] for tool in tools} == EXPECTED_TOOL_IDS,
        "missing_evidence_paths": missing_evidence,
        "missing_required_docs": missing_docs,
        "stale_active_references": stale_references,
        "branch_contract": "production-preview",
    }
    if write_receipt:
        write_json(artifacts_root() / "portfolio_check.json", payload)
    if payload["status"] != "passed":
        raise PortfolioCheckError(f"Portfolio check failed: {payload}")
    return payload
