import duckdb

from fieldforge.settings import WAREHOUSE


def test_order_lines_reach_the_fact_without_row_loss_or_invented_keys():
    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        accepted_lines = connection.execute("select count(*) from stg_order_items").fetchone()[0]
        fact_lines = connection.execute("select count(*) from fct_order_item").fetchone()[0]
        duplicate_grain = connection.execute(
            "select count(*) from (select order_id, line_number from fct_order_item "
            "group by 1,2 having count(*) > 1)"
        ).fetchone()[0]
        unresolved_products = connection.execute(
            "select count(*) from fct_order_item f left join dim_product p using(product_sk) "
            "where p.product_sk is null"
        ).fetchone()[0]
        link_status = connection.execute(
            "select order_link_status, count(*) from fct_order_item group by 1 order by 1"
        ).df()

    assert accepted_lines == fact_lines
    assert duplicate_grain == 0
    assert unresolved_products == 0
    assert set(link_status["order_link_status"]) <= {"linked", "order_not_accepted"}
    assert link_status["count_star()"].sum() == accepted_lines


def test_lines_whose_parent_order_was_quarantined_are_retained_not_guessed():
    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        orphaned = connection.execute(
            "select count(*) from fct_order_item where order_link_status = 'order_not_accepted'"
        ).fetchone()[0]
        invented_order_context = connection.execute(
            "select count(*) from fct_order_item where order_link_status = 'order_not_accepted' "
            "and (order_date_key is not null or order_status is not null or currency is not null "
            "or customer_sk is not null)"
        ).fetchone()[0]
        missing_link_context = connection.execute(
            "select count(*) from fct_order_item f "
            "left join stg_orders o on o.order_id = f.order_id "
            "where f.order_link_status = 'linked' and o.order_id is null"
        ).fetchone()[0]

    assert orphaned > 0
    assert invented_order_context == 0
    assert missing_link_context == 0


def test_order_line_variance_is_explained_by_quarantine_evidence():
    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        negative_variance = connection.execute(
            "select count(*) from mart_order_line_integrity where line_variance_cents < 0"
        ).fetchone()[0]
        unexplained = connection.execute(
            "select count(*) from mart_order_line_integrity "
            "where line_coverage_status = 'incomplete_unexplained_line'"
        ).fetchone()[0]
        orphaned_lines = connection.execute(
            "select count(*) from stg_quarantined_order_items "
            "where _rule_codes like '%ORDER_ITEM_ORPHAN%'"
        ).fetchone()[0]
        covered_orders = connection.execute(
            "select (select count(*) from mart_order_line_integrity) = "
            "(select count(*) from stg_orders)"
        ).fetchone()[0]

    assert negative_variance == 0
    assert unexplained <= orphaned_lines
    assert covered_orders


def test_date_dimension_covers_every_recognized_revenue_date():
    with duckdb.connect(str(WAREHOUSE), read_only=True) as connection:
        gaps = connection.execute(
            "select count(*) from (select date_key, lag(date_key) over (order by date_key) as previous_date_key "
            "from dim_date) where previous_date_key is not null "
            "and date_diff('day', previous_date_key, date_key) <> 1"
        ).fetchone()[0]
        revenue_dates_outside_dimension = connection.execute(
            "select count(*) from fct_revenue f left join dim_date d on d.date_key = f.recognized_date "
            "where d.date_key is null"
        ).fetchone()[0]
        spine_matches_subscription_months = connection.execute(
            "select (select count(distinct calendar_month) from dim_date) = "
            "(select count(distinct calendar_month) from mart_subscription_health)"
        ).fetchone()[0]

    assert gaps == 0
    assert revenue_dates_outside_dimension == 0
    assert spine_matches_subscription_months
