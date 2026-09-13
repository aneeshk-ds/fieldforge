import json

import duckdb
import pandas as pd
from streamlit.testing.v1 import AppTest

from dashboard.data_quality import (
    SOURCES,
    build_timeline,
    evidence_request,
    load_quality_snapshot,
    load_quarantined_record,
)
from dashboard.project_progress import acceptance_progress
from dashboard.queries import QUERIES
from fieldforge.settings import data_root, warehouse_path

DATA = data_root()


def test_acceptance_progress_is_derived_from_the_release_checklist(tmp_path):
    checklist = tmp_path / "acceptance.md"
    checklist.write_text(
        "# Gate\n\n- [x] Complete\n- [ ] Pending\n- [X] Also complete\n",
        encoding="utf-8",
    )

    assert acceptance_progress(checklist) == (2, 3)


def test_dashboard_renders_separate_software_and_learning_progress():
    app = AppTest.from_file("dashboard/app.py", default_timeout=30).run()

    assert not app.exception
    markup = "\n".join(element.value for element in app.markdown)
    assert "Private software &amp; portfolio acceptance" in markup
    assert "14/14 · 100%" in markup
    assert "Learning is tracked separately: 0/38 tools graded" in markup
    progress = app.get("progress")
    assert len(progress) == 1
    assert progress[0].value == 100


def test_dashboard_quality_snapshot_traces_to_reconciled_pipeline_outputs():
    snapshot = load_quality_snapshot(DATA)

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
    snapshot = load_quality_snapshot(DATA)
    exception = snapshot.rejected.query("record_key == 'ORD-0000028'").iloc[0]
    record = load_quarantined_record(DATA, "orders", int(exception["source_row"]))
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


def test_order_integrity_dashboard_keeps_known_and_unexplained_gaps_visible():
    with duckdb.connect(str(warehouse_path()), read_only=True) as connection:
        summary = connection.execute(QUERIES["order_line_summary"]).fetchone()
        integrity = connection.execute(QUERIES["order_line_integrity"]).df()

    incomplete = integrity.query("line_coverage_status != 'complete'")
    known = incomplete.query("line_coverage_status == 'incomplete_quarantined_line'")
    unexplained = incomplete.query("line_coverage_status == 'incomplete_unexplained_line'")

    assert len(integrity) == 1494
    assert summary == (1494, 3021, 3013, 8, 1, 2)
    assert known["order_id"].tolist() == ["ORD-0000015"]
    assert known["quarantined_lines_same_order"].tolist() == [1]
    assert set(unexplained["order_id"]) == {"ORD-0000021", "ORD-0000026"}
    assert unexplained["quarantined_lines_same_order"].eq(0).all()


def test_order_integrity_dashboard_renders_registered_line_population():
    app = AppTest.from_file("dashboard/app.py", default_timeout=30).run()

    assert not app.exception
    markup = "\n".join(element.value for element in app.markdown)
    assert "Accepted order lines" in markup
    assert "3,021" in markup
    assert "3,013 linked · 8 retained without accepted parent" in markup


def test_subscription_dashboard_query_exposes_churn_and_denominator():
    with duckdb.connect(str(warehouse_path()), read_only=True) as connection:
        subscriptions = connection.execute(QUERIES["subscriber_trend"]).df()

    premium_march = subscriptions.query(
        "plan_code == 'PREMIUM' and calendar_month == @march",
        local_dict={"march": pd.Timestamp("2026-03-01")},
    ).iloc[0]
    assert premium_march["active_subscribers"] == 88
    assert premium_march["churned_subscribers"] == 4
    assert premium_march["prior_month_active"] == 84
    assert premium_march["logo_churn_rate"] == 4 / 84


def test_revenue_dashboard_aggregates_types_within_each_currency():
    with duckdb.connect(str(warehouse_path()), read_only=True) as connection:
        trend = connection.execute(QUERIES["revenue_trend"]).df()
        attribution = connection.execute(QUERIES["revenue_attribution"]).df()
        expected_trend = connection.execute(
            """select calendar_month, currency, sum(net_revenue_cents)/100.0 net_revenue
               from mart_monthly_kpis group by 1,2 order by 1,2"""
        ).df()
        expected_attribution = connection.execute(
            """select currency,
                      100.0 * sum(attributed_net_revenue_cents)
                        / nullif(sum(net_revenue_cents), 0) attribution_rate
               from mart_monthly_kpis group by 1 order by 1"""
        ).df()

    pd.testing.assert_frame_equal(trend, expected_trend)
    pd.testing.assert_series_equal(
        attribution["currency"], expected_attribution["currency"]
    )
    pd.testing.assert_series_equal(
        attribution["attribution_rate"], expected_attribution["attribution_rate"]
    )


def test_business_dashboard_renders_logo_churn_as_a_percentage():
    app = AppTest.from_file("dashboard/app.py", default_timeout=30).run()

    assert not app.exception
    churn_specs = []
    for chart in app.get("plotly_chart"):
        spec = json.loads(chart.proto.spec)
        y_axis = spec.get("layout", {}).get("yaxis", {})
        if y_axis.get("title", {}).get("text") == "Logo churn (%)":
            churn_specs.append(spec)

    assert len(churn_specs) == 1
    churn_spec = churn_specs[0]
    assert churn_spec["layout"]["yaxis"]["ticksuffix"] == "%"
    assert {trace["name"] for trace in churn_spec["data"]} == {
        "ESSENTIALS",
        "PLUS",
        "PREMIUM",
    }
    assert all(
        "Subscriptions cancelled" in trace["hovertemplate"]
        and "Prior month-end active" in trace["hovertemplate"]
        for trace in churn_spec["data"]
    )
