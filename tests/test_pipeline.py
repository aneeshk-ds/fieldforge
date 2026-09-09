import hashlib
import json

import pandas as pd
import pytest

from fieldforge import settings
from fieldforge.generate import generate
from fieldforge.pipeline import ingest_bronze, profile_sources, resolve_identities, validate_silver

pytestmark = pytest.mark.usefixtures("isolated_data_root")


def _digest_tree(root) -> dict[str, str]:
    """Checksum every file under root so any write is detectable."""
    if not root.exists():
        return {}
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and "test-runs" not in path.parts
    }


def test_pipeline_writes_only_inside_the_isolated_root(test_run_id):
    repository_sources = settings.ROOT / "data" / "source"
    repository_artifacts = settings.ROOT / "artifacts"
    before = (_digest_tree(repository_sources), _digest_tree(repository_artifacts))

    generate()
    profile_sources()
    ingest_bronze(test_run_id)
    validate_silver()
    resolve_identities()

    after = (_digest_tree(repository_sources), _digest_tree(repository_artifacts))

    assert settings.is_isolated()
    assert settings.data_root() != settings.ROOT / "data"
    assert settings.artifacts_root() != settings.ROOT / "artifacts"
    assert (settings.source_dir() / "customers.csv").exists()
    assert before == after


def test_generation_is_reproducible():
    generate(seed=42, customers=300)
    first = (settings.source_dir() / "customers.csv").read_bytes()
    generate(seed=42, customers=300)
    assert (settings.source_dir() / "customers.csv").read_bytes() == first
    generate()


def test_no_silent_loss_and_explicit_reasons(test_run_id):
    generate()
    profile_sources()
    ingest_bronze(test_run_id)
    summary = validate_silver()
    assert all(item["reconciled"] for item in summary.values())
    assert sum(item["quarantined"] for item in summary.values()) > 0
    manifest = json.loads((settings.artifacts_root() / "synthetic_manifest.json").read_text())
    assert {name: item["quarantined"] for name, item in summary.items()} == manifest["planted_counts"]
    for source, item in summary.items():
        if item["quarantined"]:
            quarantine = pd.read_parquet(settings.quarantine_dir() / f"{source}.parquet")
            assert quarantine["_rule_codes"].str.len().gt(0).all()
            assert quarantine["_rejection_reasons"].str.len().gt(0).all()
            assert quarantine["_run_id"].eq(test_run_id).all()

    customers = pd.read_parquet(settings.silver_dir() / "customers.parquet")
    event_frames = []
    for source, event_column in (
        ("subscriptions", "start_date"),
        ("orders", "ordered_at"),
        ("tickets", "opened_at"),
    ):
        events = pd.read_parquet(settings.silver_dir() / f"{source}.parquet")
        event_frames.append(
            events[["normalized_email", event_column]].rename(columns={event_column: "event_at"})
        )
    first_events = (
        pd.concat(event_frames)
        .assign(event_at=lambda frame: pd.to_datetime(frame["event_at"], format="mixed"))
        .groupby("normalized_email", as_index=False)["event_at"]
        .min()
    )
    chronology = customers.merge(first_events, on="normalized_email", how="inner")
    assert (pd.to_datetime(chronology["created_at"]) <= chronology["event_at"]).all()


def test_identity_crosswalk_explains_every_match():
    crosswalk = resolve_identities()
    assert crosswalk["match_method"].notna().all()
    assert crosswalk["confidence"].between(0, 1).all()
    accepted = pd.read_parquet(settings.silver_dir() / "customers.parquet")
    assert len(crosswalk.query("source_system == 'customers'")) == len(accepted)


def test_profile_matches_bronze():
    report = json.loads((settings.artifacts_root() / "source_profile.json").read_text())
    for source, values in report.items():
        assert values["rows"] == len(pd.read_parquet(settings.bronze_dir() / f"{source}.parquet"))
