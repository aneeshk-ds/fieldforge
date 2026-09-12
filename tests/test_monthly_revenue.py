from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from fieldforge.reconciliation import monthly_revenue_matches

ROOT = Path(__file__).resolve().parents[1]


def render_sql(path, replacements):
    sql = path.read_text()
    for old, new in replacements.items():
        sql = sql.replace(old, new)
    return sql


@pytest.fixture
def revenue_case(tmp_path):
    invoices = [
        {
            "invoice_id": "INV-1",
            "subscription_id": "SUB-1",
            "billing_customer_id": "S-1",
            "paid_at": "2024-03-05",
            "refunded_at": "",
            "gross_amount_cents": "10000",
            "refund_amount_cents": "1000",
            "currency": "USD",
        },
        {
            "invoice_id": "INV-2",
            "subscription_id": "SUB-2",
            "billing_customer_id": "S-2",
            "paid_at": "2024-03-12",
            "refunded_at": "",
            "gross_amount_cents": "5000",
            "refund_amount_cents": "0",
            "currency": "USD",
        },
        {
            "invoice_id": "INV-3",
            "subscription_id": "SUB-2",
            "billing_customer_id": "S-2",
            "paid_at": "2024-04-02",
            "refunded_at": "2024-04-03",
            "gross_amount_cents": "2000",
            "refund_amount_cents": "2000",
            "currency": "GBP",
        },
        {
            "invoice_id": "INV-4",
            "subscription_id": "SUB-2",
            "billing_customer_id": "S-2",
            "paid_at": "2024-05-02",
            "refunded_at": "",
            "gross_amount_cents": "3000",
            "refund_amount_cents": "0",
            "currency": "CAD",
        },
    ]
    orders = [
        {
            "order_id": "ORD-1",
            "storefront_customer_id": "O-1",
            "normalized_email": "one@example.com",
            "ordered_at": "2024-03-08 12:00:00",
            "delivered_at": "2024-03-10 12:00:00",
            "status": "delivered",
            "order_amount_cents": "20000",
            "refund_amount_cents": "2000",
            "currency": "USD",
        },
        {
            "order_id": "ORD-2",
            "storefront_customer_id": "O-2",
            "normalized_email": "two@example.com",
            "ordered_at": "2024-03-09 12:00:00",
            "delivered_at": "2024-03-11 12:00:00",
            "status": "delivered",
            "order_amount_cents": "10000",
            "refund_amount_cents": "0",
            "currency": "USD",
        },
        {
            "order_id": "ORD-3",
            "storefront_customer_id": "O-1",
            "normalized_email": "one@example.com",
            "ordered_at": "2024-03-10 12:00:00",
            "delivered_at": "",
            "status": "cancelled",
            "order_amount_cents": "9000",
            "refund_amount_cents": "0",
            "currency": "CAD",
        },
        {
            "order_id": "ORD-4",
            "storefront_customer_id": "O-1",
            "normalized_email": "one@example.com",
            "ordered_at": "2024-04-10 12:00:00",
            "delivered_at": "2024-04-12 12:00:00",
            "status": "delivered",
            "order_amount_cents": "6000",
            "refund_amount_cents": "1000",
            "currency": "GBP",
        },
    ]
    crosswalk = [
        {
            "source_system": "subscriptions",
            "source_identity": "S-1",
            "customer_sk": "CUS-1",
            "match_method": "exact",
            "confidence": "1.0",
            "normalized_email": "one@example.com",
        },
        {
            "source_system": "subscriptions",
            "source_identity": "S-2",
            "customer_sk": None,
            "match_method": "unresolved",
            "confidence": "0.0",
            "normalized_email": "two@example.com",
        },
        {
            "source_system": "orders",
            "source_identity": "O-1",
            "customer_sk": "CUS-1",
            "match_method": "exact",
            "confidence": "1.0",
            "normalized_email": "one@example.com",
        },
        {
            "source_system": "orders",
            "source_identity": "O-2",
            "customer_sk": None,
            "match_method": "unresolved",
            "confidence": "0.0",
            "normalized_email": "two@example.com",
        },
    ]
    for name, rows in (
        ("invoices", invoices),
        ("orders", orders),
        ("identity_crosswalk", crosswalk),
    ):
        pq.write_table(pa.Table.from_pylist(rows), tmp_path / f"{name}.parquet")

    with duckdb.connect() as con:
        for name in ("invoices", "orders", "identity_crosswalk"):
            con.read_parquet(str(tmp_path / f"{name}.parquet")).create_view(
                f"silver_{name}"
            )
        for name in ("invoices", "orders", "identity_crosswalk"):
            sql = render_sql(
                ROOT / f"dbt/models/staging/stg_{name}.sql",
                {f"{{{{ source('silver', '{name}') }}}}": f"silver_{name}"},
            )
            con.execute(f"create table stg_{name} as {sql}")
        fact = render_sql(
            ROOT / "dbt/models/marts/fct_revenue.sql",
            {
                f"{{{{ ref('{name}') }}}}": name
                for name in (
                    "stg_invoices",
                    "stg_orders",
                    "stg_identity_crosswalk",
                )
            },
        )
        con.execute("create table fct_revenue as " + fact)
        mart = render_sql(
            ROOT / "dbt/models/marts/mart_monthly_kpis.sql",
            {"{{ ref('fct_revenue') }}": "fct_revenue"},
        )
        con.execute("create table mart_monthly_kpis as " + mart)
        yield con, tmp_path


def sql_failures(con):
    sql = render_sql(
        ROOT / "dbt/tests/assert_monthly_revenue_reconciles.sql",
        {
            "{{ source('silver', 'invoices') }}": "silver_invoices",
            "{{ source('silver', 'orders') }}": "silver_orders",
            "{{ source('silver', 'identity_crosswalk') }}": "silver_identity_crosswalk",
            "{{ ref('mart_monthly_kpis') }}": "mart_monthly_kpis",
        },
    )
    return con.execute(sql).fetchall()


def test_model_boundaries_and_independent_control(revenue_case):
    con, silver = revenue_case
    assert monthly_revenue_matches(con, silver)
    assert sql_failures(con) == []
    assert con.execute(
        """select net_revenue_cents, attributed_net_revenue_cents,
                  unattributed_net_revenue_cents, revenue_attribution_rate
           from mart_monthly_kpis
           where calendar_month=date '2024-03-01'
             and revenue_type='subscription' and currency='USD'"""
    ).fetchone() == (14000, 9000, 5000, 100.0 * 9000 / 14000)
    assert con.execute(
        """select revenue_attribution_rate from mart_monthly_kpis
           where calendar_month=date '2024-05-01'"""
    ).fetchone() == (0.0,)
    assert con.execute(
        """select revenue_attribution_rate from mart_monthly_kpis
           where calendar_month=date '2024-04-01'
             and revenue_type='subscription'"""
    ).fetchone() == (None,)
    assert con.execute(
        "select count(*) from mart_monthly_kpis where currency='CAD'"
    ).fetchone() == (1,)


@pytest.mark.parametrize(
    "mutation",
    [
        "update mart_monthly_kpis set net_revenue_cents=net_revenue_cents+1",
        "update mart_monthly_kpis set gross_revenue_cents=gross_revenue_cents+100, refund_amount_cents=refund_amount_cents+100",
        "update mart_monthly_kpis set attributed_net_revenue_cents=attributed_net_revenue_cents+100, unattributed_net_revenue_cents=unattributed_net_revenue_cents-100 where net_revenue_cents>0",
        "update mart_monthly_kpis set attributed_transactions=attributed_transactions+1, unattributed_transactions=unattributed_transactions-1",
        "update mart_monthly_kpis set purchasing_customers=purchasing_customers+1",
        "update mart_monthly_kpis set revenue_attribution_rate=12.34 where revenue_attribution_rate is not null",
        "update mart_monthly_kpis set revenue_attribution_rate=null where revenue_attribution_rate=0",
        "update mart_monthly_kpis set revenue_attribution_rate=0 where revenue_attribution_rate is null",
        "update mart_monthly_kpis set revenue_attribution_rate='NaN'::double where revenue_attribution_rate>0",
        "update mart_monthly_kpis set revenue_attribution_rate='Infinity'::double where revenue_attribution_rate>0",
        "delete from mart_monthly_kpis where revenue_type='one_off'",
        "update mart_monthly_kpis set currency='EUR' where currency='CAD'",
    ],
)
def test_checks_detect_corrupted_groups(revenue_case, mutation):
    con, silver = revenue_case
    con.execute(mutation)
    assert not monthly_revenue_matches(con, silver)
    assert sql_failures(con)


def test_checks_detect_duplicate_mart_groups(revenue_case):
    con, silver = revenue_case
    con.execute("insert into mart_monthly_kpis select * from mart_monthly_kpis limit 1")
    assert not monthly_revenue_matches(con, silver)


def test_checks_detect_duplicate_source_identities(revenue_case):
    con, silver = revenue_case
    path = silver / "identity_crosswalk.parquet"
    table = pq.read_table(path)
    pq.write_table(pa.concat_tables([table, table.slice(0, 1)]), path)
    assert not monthly_revenue_matches(con, silver)
    assert sql_failures(con)
