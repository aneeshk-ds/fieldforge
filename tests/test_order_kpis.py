from pathlib import Path

import duckdb
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from fieldforge.reconciliation import order_kpis_match

ROOT = Path(__file__).resolve().parents[1]


def render_sql(path: Path, replacements: dict[str, str]) -> str:
    sql = path.read_text()
    for old, new in replacements.items():
        sql = sql.replace(old, new)
    return sql


@pytest.fixture
def order_case(tmp_path):
    silver = tmp_path / "silver"
    quarantine = tmp_path / "quarantine"
    silver.mkdir()
    quarantine.mkdir()
    orders = [
        {
            "order_id": "ORD-1",
            "storefront_customer_id": "CUS-1",
            "normalized_email": "one@example.com",
            "ordered_at": "2026-01-01 10:00:00",
            "delivered_at": "2026-01-02 10:00:00",
            "status": "delivered",
            "order_amount_cents": "1000",
            "refund_amount_cents": "0",
            "currency": "USD",
        },
        {
            "order_id": "ORD-2",
            "storefront_customer_id": "CUS-2",
            "normalized_email": "two@example.com",
            "ordered_at": "2026-01-03 10:00:00",
            "delivered_at": "2026-01-04 10:00:00",
            "status": "delivered",
            "order_amount_cents": "1000",
            "refund_amount_cents": "0",
            "currency": "CAD",
        },
        {
            "order_id": "ORD-3",
            "storefront_customer_id": "CUS-3",
            "normalized_email": "three@example.com",
            "ordered_at": "2026-01-05 10:00:00",
            "delivered_at": "2026-01-06 10:00:00",
            "status": "delivered",
            "order_amount_cents": "500",
            "refund_amount_cents": "0",
            "currency": "GBP",
        },
    ]
    items = [
        {"order_id": "ORD-1", "line_number": "1", "product_id": "P1", "quantity": "1", "unit_price_cents": "600", "_run_id": "test"},
        {"order_id": "ORD-1", "line_number": "2", "product_id": "P2", "quantity": "2", "unit_price_cents": "200", "_run_id": "test"},
        {"order_id": "ORD-2", "line_number": "1", "product_id": "P1", "quantity": "1", "unit_price_cents": "700", "_run_id": "test"},
        {"order_id": "ORD-3", "line_number": "1", "product_id": "P3", "quantity": "2", "unit_price_cents": "100", "_run_id": "test"},
        {"order_id": "ORD-X", "line_number": "1", "product_id": "P4", "quantity": "1", "unit_price_cents": "900", "_run_id": "test"},
    ]
    quarantined = [
        {
            "order_id": "ORD-2",
            "line_number": "2",
            "product_id": "P2",
            "quantity": "1",
            "unit_price_cents": "300",
            "_rule_codes": "ORDER_ITEM_QUANTITY_INVALID",
            "_rejection_reasons": "quantity is invalid",
            "_raw_key": "ORD-2|2",
            "_run_id": "test",
        },
        {
            "order_id": "ORD-MISSING",
            "line_number": "2",
            "product_id": "P3",
            "quantity": "1",
            "unit_price_cents": "300",
            "_rule_codes": "ORDER_ITEM_ORPHAN",
            "_rejection_reasons": "order is missing",
            "_raw_key": "ORD-MISSING|2",
            "_run_id": "test",
        },
    ]
    pq.write_table(pa.Table.from_pylist(orders), silver / "orders.parquet")
    pq.write_table(pa.Table.from_pylist(items), silver / "order_items.parquet")
    pq.write_table(pa.Table.from_pylist(quarantined), quarantine / "order_items.parquet")

    with duckdb.connect() as con:
        con.read_parquet(str(silver / "orders.parquet")).create_view("silver_orders")
        con.read_parquet(str(silver / "order_items.parquet")).create_view("silver_order_items")
        con.read_parquet(str(quarantine / "order_items.parquet")).create_view(
            "quarantine_order_items"
        )
        for model, source in (
            ("stg_orders", "silver_orders"),
            ("stg_order_items", "silver_order_items"),
            ("stg_quarantined_order_items", "quarantine_order_items"),
        ):
            source_name = "quarantine" if model == "stg_quarantined_order_items" else "silver"
            table_name = "order_items" if "order_items" in model else "orders"
            sql = render_sql(
                ROOT / f"dbt/models/staging/{model}.sql",
                {f"{{{{ source('{source_name}', '{table_name}') }}}}": source},
            )
            con.execute(f"create table {model} as {sql}")
        dim_product = render_sql(
            ROOT / "dbt/models/marts/dim_product.sql",
            {"{{ ref('stg_order_items') }}": "stg_order_items"},
        )
        con.execute("create table dim_product as " + dim_product)
        con.execute(
            """create table stg_identity_crosswalk as
               select * from (values
                 ('orders', 'CUS-1', 'SK-1'),
                 ('orders', 'CUS-2', 'SK-2'),
                 ('orders', 'CUS-3', 'SK-3')
               ) as x(source_system, source_identity, customer_sk)"""
        )
        fact = render_sql(
            ROOT / "dbt/models/marts/fct_order_item.sql",
            {
                "{{ ref('stg_order_items') }}": "stg_order_items",
                "{{ ref('stg_orders') }}": "stg_orders",
                "{{ ref('stg_identity_crosswalk') }}": "stg_identity_crosswalk",
                "{{ ref('dim_product') }}": "dim_product",
            },
        )
        con.execute("create table fct_order_item as " + fact)
        mart = render_sql(
            ROOT / "dbt/models/marts/mart_order_line_integrity.sql",
            {
                "{{ ref('stg_orders') }}": "stg_orders",
                "{{ ref('fct_order_item') }}": "fct_order_item",
                "{{ ref('stg_quarantined_order_items') }}": "stg_quarantined_order_items",
            },
        )
        con.execute("create table mart_order_line_integrity as " + mart)
        yield con, silver, quarantine


def sql_failures(con):
    sql = render_sql(
        ROOT / "dbt/tests/assert_order_kpis_reconcile.sql",
        {
            "{{ source('silver', 'orders') }}": "silver_orders",
            "{{ source('silver', 'order_items') }}": "silver_order_items",
            "{{ source('quarantine', 'order_items') }}": "quarantine_order_items",
            "{{ ref('fct_order_item') }}": "fct_order_item",
            "{{ ref('mart_order_line_integrity') }}": "mart_order_line_integrity",
        },
    )
    return con.execute(sql).fetchall()


def test_order_models_and_independent_controls_cover_every_accepted_line(order_case):
    con, silver, quarantine = order_case
    assert order_kpis_match(con, silver, quarantine)
    assert sql_failures(con) == []
    assert con.execute(
        "select order_link_status, count(*) from fct_order_item group by 1 order by 1"
    ).fetchall() == [("linked", 4), ("order_not_accepted", 1)]
    assert con.execute(
        """select order_id, line_variance_cents, accepted_lines,
                  quarantined_lines_same_order, line_coverage_status
           from mart_order_line_integrity order by order_id"""
    ).fetchall() == [
        ("ORD-1", 0, 2, 0, "complete"),
        ("ORD-2", 300, 1, 1, "incomplete_quarantined_line"),
        ("ORD-3", 300, 1, 0, "incomplete_unexplained_line"),
    ]


@pytest.mark.parametrize(
    "mutation",
    [
        "update fct_order_item set extended_amount_cents=extended_amount_cents+1 where order_id='ORD-1' and line_number=1",
        "update fct_order_item set order_link_status='linked' where order_id='ORD-X'",
        "delete from fct_order_item where order_id='ORD-X'",
        "update mart_order_line_integrity set line_variance_cents=line_variance_cents+1 where order_id='ORD-2'",
        "update mart_order_line_integrity set accepted_lines=accepted_lines+1 where order_id='ORD-2'",
        "update mart_order_line_integrity set quarantined_lines_same_order=0 where order_id='ORD-2'",
        "update mart_order_line_integrity set line_coverage_status='complete' where order_id='ORD-3'",
        "delete from mart_order_line_integrity where order_id='ORD-3'",
    ],
)
def test_order_controls_detect_corrupted_outputs(order_case, mutation):
    con, silver, quarantine = order_case
    con.execute(mutation)
    assert not order_kpis_match(con, silver, quarantine)
    assert sql_failures(con)


@pytest.mark.parametrize(
    "table",
    ["fct_order_item", "mart_order_line_integrity"],
)
def test_python_control_detects_duplicate_output_grain(order_case, table):
    con, silver, quarantine = order_case
    con.execute(f"insert into {table} select * from {table} limit 1")
    assert not order_kpis_match(con, silver, quarantine)
