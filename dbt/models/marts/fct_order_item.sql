-- Grain: one row per accepted order line (order_id, line_number).
-- Every accepted line is retained. A line whose parent order was quarantined
-- keeps order_link_status = 'order_not_accepted' with null order attributes
-- instead of being dropped or given an invented order.
with lines as (
  select * from {{ ref('stg_order_items') }}
), orders as (
  select * from {{ ref('stg_orders') }}
), crosswalk as (
  select source_identity, customer_sk
  from {{ ref('stg_identity_crosswalk') }}
  where source_system = 'orders'
)
select
  substr(sha256('order_item|' || l.order_id || '|' || cast(l.line_number as varchar)), 1, 16) as order_item_sk,
  l.order_id,
  l.line_number,
  p.product_sk,
  l.product_id,
  x.customer_sk,
  case when x.customer_sk is null then 'unattributed' else 'attributed' end as attribution_status,
  case when o.order_id is null then 'order_not_accepted' else 'linked' end as order_link_status,
  cast(o.ordered_at as date) as order_date_key,
  o.status as order_status,
  o.currency,
  l.quantity,
  l.unit_price_cents,
  l.extended_amount_cents
from lines l
left join orders o on o.order_id = l.order_id
left join {{ ref('dim_product') }} p on p.product_id = l.product_id
left join crosswalk x on x.source_identity = o.storefront_customer_id
