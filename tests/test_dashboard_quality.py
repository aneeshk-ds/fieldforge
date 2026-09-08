from pathlib import Path

from dashboard.data_quality import SOURCES, load_quality_snapshot

ROOT = Path(__file__).resolve().parents[1]


def test_dashboard_quality_snapshot_traces_to_reconciled_pipeline_outputs():
    snapshot = load_quality_snapshot(ROOT)

    assert snapshot.reconciled
    assert snapshot.received == snapshot.accepted + snapshot.quarantined
    assert snapshot.sources["reconciled"].all()
    assert snapshot.sources["received"].sum() == snapshot.received
    assert snapshot.sources["accepted"].sum() == snapshot.accepted
    assert snapshot.sources["quarantined"].sum() == snapshot.quarantined
    assert len(snapshot.rejected) == snapshot.quarantined
    assert set(snapshot.sources["source"]) == {source for source, _ in SOURCES}
    assert snapshot.rejected["record_key"].notna().all()
    assert snapshot.rejected["rule_code"].str.len().gt(0).all()
    assert snapshot.rejected["reason"].str.len().gt(0).all()
    assert snapshot.reasons["failures"].sum() >= snapshot.quarantined
