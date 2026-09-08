-- Grain: one row per recognized revenue transaction (invoice or non-cancelled order).
-- Financially valid transactions stay in the fact even when identity is unresolved:
-- customer_sk is null and attribution_status is 'unattributed'.
with crosswalk as (
  select source_system, source_identity, customer_sk from {{ ref('stg_identity_crosswalk') }}
), subscription_revenue as (
  select i.invoice_id as revenue_id, x.customer_sk, i.paid_at as recognized_date,
    'subscription' as revenue_type, i.currency,
    case when x.customer_sk is null then 'unattributed' else 'attributed' end as attribution_status,
    i.gross_amount_cents,
    i.refund_amount_cents, i.gross_amount_cents - i.refund_amount_cents as net_revenue_cents
  from {{ ref('stg_invoices') }} i
  left join crosswalk x
    on x.source_system = 'subscriptions' and x.source_identity = i.billing_customer_id
), order_revenue as (
  select o.order_id as revenue_id, x.customer_sk, cast(o.ordered_at as date) as recognized_date,
    'one_off' as revenue_type, o.currency,
    case when x.customer_sk is null then 'unattributed' else 'attributed' end as attribution_status,
    o.order_amount_cents as gross_amount_cents, o.refund_amount_cents,
    o.order_amount_cents - o.refund_amount_cents as net_revenue_cents
  from {{ ref('stg_orders') }} o
  left join crosswalk x
    on x.source_system = 'orders' and x.source_identity = o.storefront_customer_id
  where o.status <> 'cancelled'
)
select * from subscription_revenue union all select * from order_revenue
