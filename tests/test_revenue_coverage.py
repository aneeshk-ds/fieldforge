import duckdb

from fieldforge.settings import warehouse_path


def test_company_revenue_keeps_unattributed_transactions_visible():
    with duckdb.connect(str(warehouse_path()), read_only=True) as connection:
        source_subscription = connection.execute(
            "select sum(gross_amount_cents-refund_amount_cents) from stg_invoices"
        ).fetchone()[0]
        fact_subscription = connection.execute(
            "select sum(net_revenue_cents) from fct_revenue where revenue_type='subscription'"
        ).fetchone()[0]
        source_orders = connection.execute(
            "select sum(order_amount_cents-refund_amount_cents) from stg_orders "
            "where status <> 'cancelled'"
        ).fetchone()[0]
        fact_orders = connection.execute(
            "select sum(net_revenue_cents) from fct_revenue where revenue_type='one_off'"
        ).fetchone()[0]
        unattributed = connection.execute(
            "select currency, count(*) transactions, sum(net_revenue_cents) net_revenue_cents "
            "from fct_revenue where attribution_status='unattributed' group by 1 order by 1"
        ).df()

    assert source_subscription == fact_subscription
    assert source_orders == fact_orders
    assert unattributed["transactions"].sum() > 0
    assert unattributed["net_revenue_cents"].sum() > 0


def test_revenue_attribution_partition_and_customer_keys_are_consistent():
    with duckdb.connect(str(warehouse_path()), read_only=True) as connection:
        inconsistent_facts = connection.execute(
            "select count(*) from fct_revenue where "
            "(attribution_status='attributed' and customer_sk is null) or "
            "(attribution_status='unattributed' and customer_sk is not null)"
        ).fetchone()[0]
        inconsistent_marts = connection.execute(
            "select count(*) from mart_monthly_kpis where "
            "net_revenue_cents <> attributed_net_revenue_cents + unattributed_net_revenue_cents "
            "or transactions <> attributed_transactions + unattributed_transactions"
        ).fetchone()[0]

    assert inconsistent_facts == 0
    assert inconsistent_marts == 0
