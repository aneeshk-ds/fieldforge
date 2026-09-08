-- An order whose accepted lines do not reconcile to its header amount must be
-- explainable by quarantined lines. Orphaned lines lose their parent order id,
-- so the number of unexplained orders can never exceed the orphaned line count.
select unexplained_orders, orphaned_lines
from (
  select
    (
      select count(*) from {{ ref('mart_order_line_integrity') }}
      where line_coverage_status = 'incomplete_unexplained_line'
    ) as unexplained_orders,
    (
      select count(*) from {{ ref('stg_quarantined_order_items') }}
      where _rule_codes like '%ORDER_ITEM_ORPHAN%'
    ) as orphaned_lines
)
where unexplained_orders > orphaned_lines
