-- Rebuild the accepted-line population and order-integrity measures directly
-- from governed sources so shared fact/mart defects cannot pass unnoticed.
with accepted_orders as (
  select
    order_id,
    cast(ordered_at as date) as order_date,
    status as order_status,
    cast(order_amount_cents as bigint) as header_amount_cents,
    currency
  from {{ source('silver', 'orders') }}
), accepted_items as (
  select
    order_id,
    cast(line_number as bigint) as line_number,
    cast(quantity as bigint) * cast(unit_price_cents as bigint) as extended_amount_cents
  from {{ source('silver', 'order_items') }}
), expected_fact as (
  select
    i.order_id,
    i.line_number,
    i.extended_amount_cents,
    case when o.order_id is null then 'order_not_accepted' else 'linked' end as order_link_status
  from accepted_items i
  left join accepted_orders o using (order_id)
), fact_failures as (
  select
    coalesce(e.order_id, a.order_id) as record_key,
    'accepted_order_lines' as check_name
  from expected_fact e
  full outer join {{ ref('fct_order_item') }} a using (order_id, line_number)
  where e.extended_amount_cents is distinct from a.extended_amount_cents
     or e.order_link_status is distinct from a.order_link_status
), line_totals as (
  select
    i.order_id,
    count(*) as accepted_lines,
    sum(i.extended_amount_cents) as accepted_line_amount_cents
  from accepted_items i
  join accepted_orders o using (order_id)
  group by i.order_id
), quarantined_lines as (
  select order_id, count(*) as quarantined_lines_same_order
  from {{ source('quarantine', 'order_items') }}
  group by order_id
), expected_mart as (
  select
    o.order_id,
    o.order_date,
    o.currency,
    o.order_status,
    o.header_amount_cents,
    coalesce(l.accepted_line_amount_cents, 0) as accepted_line_amount_cents,
    o.header_amount_cents - coalesce(l.accepted_line_amount_cents, 0) as line_variance_cents,
    coalesce(l.accepted_lines, 0) as accepted_lines,
    coalesce(q.quarantined_lines_same_order, 0) as quarantined_lines_same_order,
    case
      when o.header_amount_cents = coalesce(l.accepted_line_amount_cents, 0) then 'complete'
      when coalesce(q.quarantined_lines_same_order, 0) > 0 then 'incomplete_quarantined_line'
      else 'incomplete_unexplained_line'
    end as line_coverage_status
  from accepted_orders o
  left join line_totals l using (order_id)
  left join quarantined_lines q using (order_id)
), mart_failures as (
  select
    coalesce(e.order_id, a.order_id) as record_key,
    'order_integrity' as check_name
  from expected_mart e
  full outer join {{ ref('mart_order_line_integrity') }} a using (order_id)
  where e.order_date is distinct from a.order_date
     or e.currency is distinct from a.currency
     or e.order_status is distinct from a.order_status
     or e.header_amount_cents is distinct from a.header_amount_cents
     or e.accepted_line_amount_cents is distinct from a.accepted_line_amount_cents
     or e.line_variance_cents is distinct from a.line_variance_cents
     or e.accepted_lines is distinct from a.accepted_lines
     or e.quarantined_lines_same_order is distinct from a.quarantined_lines_same_order
     or e.line_coverage_status is distinct from a.line_coverage_status
)
select * from fact_failures
union all
select * from mart_failures
