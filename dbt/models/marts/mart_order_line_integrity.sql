-- Grain: one row per accepted order.
-- Compares the order header amount with the accepted order lines and states
-- whether a difference is explained by a quarantined line on the same order.
with accepted_orders as (
  select order_id, cast(ordered_at as date) as order_date, currency, status, order_amount_cents
  from {{ ref('stg_orders') }}
), line_totals as (
  select order_id, count(*) as accepted_lines, sum(extended_amount_cents) as accepted_line_amount_cents
  from {{ ref('fct_order_item') }}
  where order_link_status = 'linked'
  group by order_id
), quarantined_lines as (
  select order_id, count(*) as quarantined_lines
  from {{ ref('stg_quarantined_order_items') }}
  group by order_id
)
select
  o.order_id,
  o.order_date,
  o.currency,
  o.status as order_status,
  o.order_amount_cents as header_amount_cents,
  coalesce(l.accepted_line_amount_cents, 0) as accepted_line_amount_cents,
  o.order_amount_cents - coalesce(l.accepted_line_amount_cents, 0) as line_variance_cents,
  coalesce(l.accepted_lines, 0) as accepted_lines,
  coalesce(q.quarantined_lines, 0) as quarantined_lines_same_order,
  case
    when o.order_amount_cents = coalesce(l.accepted_line_amount_cents, 0) then 'complete'
    when coalesce(q.quarantined_lines, 0) > 0 then 'incomplete_quarantined_line'
    else 'incomplete_unexplained_line'
  end as line_coverage_status
from accepted_orders o
left join line_totals l on l.order_id = o.order_id
left join quarantined_lines q on q.order_id = o.order_id
