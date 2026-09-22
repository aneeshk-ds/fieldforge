import json
from pathlib import Path

import pandas as pd
import pytest

from fieldforge.contracts import SourceContractError, load_source_contracts, validate_source_frame
from fieldforge.generate import generate
from fieldforge.pipeline import SOURCES, ingest_bronze
from fieldforge.settings import artifacts_root, source_dir

pytestmark = pytest.mark.usefixtures("isolated_data_root")


def test_all_six_source_contracts_execute_before_bronze_ingestion():
    generate(seed=20260907, customers=500)
    ingest_bronze("contract-test")

    receipt = json.loads((artifacts_root() / "source_contract_validation.json").read_text())
    assert set(receipt) == set(SOURCES)
    assert all(receipt[source]["status"] == "passed" for source in SOURCES)
    assert all(receipt[source]["engine"] == "Pandera" for source in SOURCES)
    assert all(receipt[source]["registry_loader"] == "yaml.safe_load" for source in SOURCES)


@pytest.mark.parametrize("mutation", ["missing", "extra", "reordered"])
def test_source_contract_rejects_structural_drift(mutation):
    generate(seed=20260907, customers=500)
    frame = pd.read_csv(source_dir() / "orders.csv", dtype=str, keep_default_na=False)
    if mutation == "missing":
        frame = frame.drop(columns=["currency"])
    elif mutation == "extra":
        frame["unexpected"] = "x"
    else:
        frame = frame[list(reversed(frame.columns))]

    with pytest.raises(SourceContractError, match="structural contract"):
        validate_source_frame("orders", frame)


def test_contract_registry_rejects_unsafe_yaml(tmp_path: Path):
    registry = tmp_path / "unsafe.yml"
    registry.write_text("!!python/object/apply:os.system ['echo unsafe']", encoding="utf-8")

    with pytest.raises(SourceContractError, match="Cannot load source contracts"):
        load_source_contracts(registry)


def test_contract_registry_rejects_invalid_primary_key(tmp_path: Path):
    registry = tmp_path / "bad.yml"
    registry.write_text(
        "version: 1\nsources:\n  orders:\n    primary_key: missing\n    columns: [order_id]\n",
        encoding="utf-8",
    )

    with pytest.raises(SourceContractError, match="invalid primary key"):
        load_source_contracts(registry)
