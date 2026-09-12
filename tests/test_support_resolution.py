from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from fieldforge.reconciliation import support_resolution_matches


@pytest.fixture
def resolution_case(tmp_path):
    # Purpose-built boundary cases: half an hour crossing month end, instant completion,
    # unresolved records represented both ways, and an all-unresolved group.
    records = [
        {"opened_at": "2025-09-30 23:45:00", "resolved_at": "2025-10-01 00:15:00", "category": "account"},
        {"opened_at": "2025-09-02 10:00:00", "resolved_at": "2025-09-02 10:00:00", "category": "account"},
        {"opened_at": "2025-09-04 08:16:00", "resolved_at": "", "category": "account"},
        {"opened_at": "2025-09-05 08:16:00", "resolved_at": None, "category": "account"},
        {"opened_at": "2025-10-05 08:16:00", "resolved_at": None, "category": "billing"},
    ]
    path = tmp_path / "tickets.parquet"
    pq.write_table(pa.Table.from_pylist(records), path)
    with duckdb.connect() as con:
        con.read_parquet(str(path)).create_view("silver_tickets")
        con.execute("create view stg_tickets as select cast(opened_at as timestamp) opened_at, try_cast(nullif(resolved_at,'') as timestamp) resolved_at, category, null::integer csat from silver_tickets")
        model = (Path(__file__).resolve().parents[1] / "dbt/models/marts/mart_support_health.sql").read_text()
        con.execute("create table mart_support_health as " + model.replace("{{ ref('stg_tickets') }}", "stg_tickets"))
        yield con, path


def test_model_preserves_fractional_zero_and_unknown_durations(resolution_case):
    con, path = resolution_case
    assert con.execute("select ticket_count, resolved_ticket_count, avg_resolution_hours from mart_support_health order by calendar_month").fetchall() == [(4, 2, 0.25), (1, 0, None)]
    assert support_resolution_matches(con, path)
    test_sql = (Path(__file__).resolve().parents[1] / "dbt/tests/assert_support_resolution_reconciles.sql").read_text()
    sql = test_sql.replace("{{ source('silver', 'tickets') }}", "silver_tickets").replace("{{ ref('mart_support_health') }}", "mart_support_health")
    assert con.execute(sql).fetchall() == []
    con.execute("update mart_support_health set avg_resolution_hours=0 where resolved_ticket_count=0")
    assert len(con.execute(sql).fetchall()) == 1


@pytest.mark.parametrize("mutation", [
    "update mart_support_health set avg_resolution_hours=0.125 where category='account'",
    "update mart_support_health set resolved_ticket_count=4 where category='account'",
    "update mart_support_health set avg_resolution_hours=0 where category='billing'",
    "update mart_support_health set avg_resolution_hours='NaN'::double where category='account'",
    "update mart_support_health set avg_resolution_hours=null where category='account'",
    "delete from mart_support_health where category='billing'",
    "insert into mart_support_health select * from mart_support_health where category='billing'",
])
def test_resolution_control_rejects_misleading_outputs(resolution_case, mutation):
    con, path = resolution_case
    con.execute(mutation)
    assert not support_resolution_matches(con, path)
