with subscription_revenue as (
  select i.invoice_id as revenue_id, x.customer_sk, i.paid_at as recognized_date,
    'subscription' as revenue_type, i.currency, i.gross_amount_cents,
    i.refund_amount_cents, i.gross_amount_cents - i.refund_amount_cents as net_revenue_cents
  from {{ ref('stg_invoices') }} i
  join read_parquet('data/silver/identity_crosswalk.parquet') x
    on x.source_system = 'subscriptions' and x.source_identity = i.billing_customer_id
  where x.customer_sk is not null
), order_revenue as (
  select o.order_id, x.customer_sk, cast(o.ordered_at as date), 'one_off', o.currency,
    o.order_amount_cents, o.refund_amount_cents,
    o.order_amount_cents - o.refund_amount_cents
  from {{ ref('stg_orders') }} o
  join read_parquet('data/silver/identity_crosswalk.parquet') x
    on x.source_system = 'orders' and x.source_identity = o.storefront_customer_id
  where o.status <> 'cancelled' and x.customer_sk is not null
)
select * from subscription_revenue union all select * from order_revenue
