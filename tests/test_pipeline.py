import json

import pandas as pd

from fieldforge.generate import generate
from fieldforge.pipeline import ingest_bronze, profile_sources, resolve_identities, validate_silver
from fieldforge.settings import ARTIFACTS, BRONZE, QUARANTINE, SILVER, SOURCE


def test_generation_is_reproducible():
    generate(seed=42, customers=300)
    first = (SOURCE / "customers.csv").read_bytes()
    generate(seed=42, customers=300)
    assert (SOURCE / "customers.csv").read_bytes() == first
    generate()


def test_no_silent_loss_and_explicit_reasons():
    generate()
    profile_sources()
    ingest_bronze("test-run")
    summary = validate_silver()
    assert all(item["reconciled"] for item in summary.values())
    assert sum(item["quarantined"] for item in summary.values()) > 0
    manifest = json.loads((ARTIFACTS / "synthetic_manifest.json").read_text())
    assert {name: item["quarantined"] for name, item in summary.items()} == manifest["planted_counts"]
    for source, item in summary.items():
        if item["quarantined"]:
            quarantine = pd.read_parquet(QUARANTINE / f"{source}.parquet")
            assert quarantine["_rule_codes"].str.len().gt(0).all()
            assert quarantine["_rejection_reasons"].str.len().gt(0).all()
            assert quarantine["_run_id"].eq("test-run").all()


def test_identity_crosswalk_explains_every_match():
    crosswalk = resolve_identities()
    assert crosswalk["match_method"].notna().all()
    assert crosswalk["confidence"].between(0, 1).all()
    accepted = pd.read_parquet(SILVER / "customers.parquet")
    assert len(crosswalk.query("source_system == 'customers'")) == len(accepted)


def test_profile_matches_bronze():
    report = json.loads((ARTIFACTS / "source_profile.json").read_text())
    for source, values in report.items():
        assert values["rows"] == len(pd.read_parquet(BRONZE / f"{source}.parquet"))
