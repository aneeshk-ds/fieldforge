from pathlib import Path

import pandas as pd

from dashboard.data_quality import (
    SOURCES,
    build_timeline,
    evidence_request,
    load_quality_snapshot,
    load_quarantined_record,
)

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


def test_order_investigation_preserves_evidence_and_exposes_contract_gap():
    snapshot = load_quality_snapshot(ROOT)
    exception = snapshot.rejected.query("record_key == 'ORD-0000028'").iloc[0]
    record = load_quarantined_record(ROOT, "orders", int(exception["source_row"]))
    timeline = build_timeline("orders", record)

    assert record["order_id"] == "ORD-0000028"
    assert record["_rule_codes"] == "ORDER_DATES_INVALID"
    assert pd.Timestamp(record["delivered_at"]) < pd.Timestamp(record["ordered_at"])
    assert timeline[1] == {
        "field": "dispatched_at",
        "label": "Dispatched",
        "value": "Not supplied",
        "state": "absent",
    }
    assert "timestamps, timezones, event IDs, and audit history" in evidence_request(record)
