from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from fieldforge.reconciliation import logo_churn_matches

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def churn_case(tmp_path):
    records = [
        {"plan_code": "A", "start_date": "2024-01-01", "cancelled_at": "2024-01-31"},
        {"plan_code": "A", "start_date": "2024-01-05", "cancelled_at": "2024-02-10"},
        {"plan_code": "B", "start_date": "2023-12-01", "cancelled_at": None},
        {"plan_code": "B", "start_date": "2024-02-02", "cancelled_at": "2024-02-05"},
        {"plan_code": "B", "start_date": "2024-02-03", "cancelled_at": "2024-02-06"},
        {"plan_code": "C", "start_date": "2024-03-01", "cancelled_at": "2024-03-10"},
        {"plan_code": "D", "start_date": "2024-02-29", "cancelled_at": "2024-02-29"},
    ]
    pq.write_table(pa.Table.from_pylist(records), tmp_path / "subscriptions.parquet")
    # Other accepted sources, not subscription dates alone, extend the reporting window.
    for source, field, value in [("invoices", "paid_at", "2023-11-30"),
                                 ("orders", "ordered_at", "2024-04-15 12:00:00"),
                                 ("tickets", "opened_at", "2024-05-02 00:00:00")]:
        pq.write_table(pa.Table.from_pylist([{field: value}]), tmp_path / f"{source}.parquet")
    with duckdb.connect() as con:
        con.read_parquet(str(tmp_path / "subscriptions.parquet")).create_view("silver_subscriptions")
        con.execute("create view stg_subscriptions as select plan_code, cast(start_date as date) start_date, try_cast(cancelled_at as date) cancelled_at from silver_subscriptions")
        con.execute("create table dim_date as select unnest(generate_series(date '2023-11-01', date '2024-05-01', interval 1 month))::date calendar_month")
        model = (ROOT / "dbt/models/marts/mart_subscription_health.sql").read_text()
        for name in ("dim_date", "stg_subscriptions"):
            model = model.replace("{{ ref('" + name + "') }}", name)
        con.execute("create table mart_subscription_health as " + model)
        yield con, tmp_path


def sql_failures(con):
    sql = (ROOT / "dbt/tests/assert_logo_churn_reconciles.sql").read_text()
    sql = sql.replace("{{ source('silver', 'subscriptions') }}", "silver_subscriptions")
    for name in ("dim_date", "mart_subscription_health"):
        sql = sql.replace("{{ ref('" + name + "') }}", name)
    return con.execute(sql).fetchall()


def test_model_boundary_rates_and_independent_control(churn_case):
    con, silver = churn_case
    assert logo_churn_matches(con, silver)
    assert sql_failures(con) == []
    assert con.execute("select active_subscribers, churned_subscribers, logo_churn_rate from mart_subscription_health where plan_code='A' and calendar_month=date '2024-01-01'").fetchone() == (2, 1, None)
    assert con.execute("select logo_churn_rate from mart_subscription_health where plan_code='A' and calendar_month=date '2024-02-01'").fetchone() == (0.5,)
    assert con.execute("select logo_churn_rate from mart_subscription_health where plan_code='B' and calendar_month=date '2024-02-01'").fetchone() == (2.0,)
    assert con.execute("select active_subscribers, churned_subscribers from mart_subscription_health where plan_code='D' and calendar_month=date '2024-02-01'").fetchone() == (1, 1)
    assert con.execute("select logo_churn_rate from mart_subscription_health where plan_code='D' and calendar_month=date '2024-03-01'").fetchone() == (0.0,)


@pytest.mark.parametrize("mutation", [
    "update mart_subscription_health set logo_churn_rate=0 where logo_churn_rate is null",
    "update mart_subscription_health set logo_churn_rate=null where logo_churn_rate > 0",
    "update mart_subscription_health set logo_churn_rate='NaN'::double where logo_churn_rate > 0",
    "update mart_subscription_health set logo_churn_rate='Infinity'::double where logo_churn_rate > 0",
    "update mart_subscription_health set logo_churn_rate=0.25 where logo_churn_rate=0.5",
    "update mart_subscription_health set active_subscribers=active_subscribers+1",
    "update mart_subscription_health set churned_subscribers=null",
    "update mart_subscription_health set churned_subscribers=case when calendar_month=date '2024-01-01' then 2 else 0 end where plan_code='A' and calendar_month in (date '2024-01-01',date '2024-02-01')",
    "delete from mart_subscription_health where plan_code='A'",
    "delete from mart_subscription_health where calendar_month=date '2024-04-01'",
    "insert into mart_subscription_health values (date '2024-06-01', 'A', 0, 0, null)",
    "update mart_subscription_health set plan_code='unexpected' where plan_code='A'",
])
def test_churn_checks_detect_corrupted_groups(churn_case, mutation):
    con, silver = churn_case
    con.execute(mutation)
    assert not logo_churn_matches(con, silver)
    assert sql_failures(con)


def test_independent_control_catches_duplicate_groups(churn_case):
    con, silver = churn_case
    con.execute("insert into mart_subscription_health select * from mart_subscription_health limit 1")
    assert not logo_churn_matches(con, silver)


def test_independent_window_catches_shared_dbt_spine_defect(churn_case):
    con, silver = churn_case
    con.execute("delete from dim_date where calendar_month=date '2024-05-01'")
    con.execute("delete from mart_subscription_health where calendar_month=date '2024-05-01'")
    assert sql_failures(con) == []  # A shared dimension can hide the same missing month.
    assert not logo_churn_matches(con, silver)


def test_no_subscriptions_has_no_plan_groups(churn_case):
    con, silver = churn_case
    table = pq.read_table(silver / "subscriptions.parquet").slice(0, 0)
    pq.write_table(table, silver / "subscriptions.parquet")
    con.execute("delete from mart_subscription_health")
    assert logo_churn_matches(con, silver)


def test_all_sources_empty(churn_case):
    con, silver = churn_case
    for path in silver.glob("*.parquet"):
        table = pq.read_table(path).slice(0, 0)
        pq.write_table(table, path)
    con.execute("delete from mart_subscription_health")
    assert logo_churn_matches(con, silver)
