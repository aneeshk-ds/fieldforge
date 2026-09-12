with crosswalk as (
  select source_system, source_identity, any_value(customer_sk) customer_sk
  from {{ source('silver', 'identity_crosswalk') }}
  group by 1,2
), source_revenue as (
  select invoice_id revenue_id, cast(paid_at as date) recognized_date,
    'subscription' revenue_type, currency,
    cast(gross_amount_cents as bigint) gross_amount_cents,
    cast(refund_amount_cents as bigint) refund_amount_cents,
    x.customer_sk
  from {{ source('silver', 'invoices') }} i
  left join crosswalk x
    on x.source_system='subscriptions' and x.source_identity=i.billing_customer_id
  union all
  select order_id, cast(ordered_at as date), 'one_off', currency,
    cast(order_amount_cents as bigint), cast(refund_amount_cents as bigint),
    x.customer_sk
  from {{ source('silver', 'orders') }} o
  left join crosswalk x
    on x.source_system='orders' and x.source_identity=o.storefront_customer_id
  where status <> 'cancelled'
), expected as (
  select date_trunc('month', recognized_date)::date calendar_month,
    revenue_type, currency, count(*) transactions,
    sum(gross_amount_cents) gross_revenue_cents,
    sum(refund_amount_cents) refund_amount_cents,
    sum(gross_amount_cents-refund_amount_cents) net_revenue_cents,
    coalesce(sum(gross_amount_cents-refund_amount_cents)
      filter(where customer_sk is not null),0) attributed_net_revenue_cents,
    coalesce(sum(gross_amount_cents-refund_amount_cents)
      filter(where customer_sk is null),0) unattributed_net_revenue_cents,
    count(*) filter(where customer_sk is not null) attributed_transactions,
    count(*) filter(where customer_sk is null) unattributed_transactions,
    100.0 * coalesce(sum(gross_amount_cents-refund_amount_cents)
      filter(where customer_sk is not null),0)
      / nullif(sum(gross_amount_cents-refund_amount_cents),0) revenue_attribution_rate,
    count(distinct customer_sk) purchasing_customers
  from source_revenue group by 1,2,3
), comparison as (
  select coalesce(e.calendar_month,a.calendar_month) calendar_month,
    coalesce(e.revenue_type,a.revenue_type) revenue_type,
    coalesce(e.currency,a.currency) currency,
    e.calendar_month e_calendar_month, a.calendar_month a_calendar_month,
    e.transactions e_transactions, a.transactions a_transactions,
    e.gross_revenue_cents e_gross_revenue_cents,
    a.gross_revenue_cents a_gross_revenue_cents,
    e.refund_amount_cents e_refund_amount_cents,
    a.refund_amount_cents a_refund_amount_cents,
    e.net_revenue_cents e_net_revenue_cents,
    a.net_revenue_cents a_net_revenue_cents,
    e.attributed_net_revenue_cents e_attributed_net_revenue_cents,
    a.attributed_net_revenue_cents a_attributed_net_revenue_cents,
    e.unattributed_net_revenue_cents e_unattributed_net_revenue_cents,
    a.unattributed_net_revenue_cents a_unattributed_net_revenue_cents,
    e.attributed_transactions e_attributed_transactions,
    a.attributed_transactions a_attributed_transactions,
    e.unattributed_transactions e_unattributed_transactions,
    a.unattributed_transactions a_unattributed_transactions,
    e.revenue_attribution_rate e_revenue_attribution_rate,
    a.revenue_attribution_rate a_revenue_attribution_rate,
    e.purchasing_customers e_purchasing_customers,
    a.purchasing_customers a_purchasing_customers
  from expected e full outer join {{ ref('mart_monthly_kpis') }} a
    using(calendar_month,revenue_type,currency)
), duplicate_crosswalk as (
  select source_system, source_identity from {{ source('silver', 'identity_crosswalk') }}
  group by 1,2 having count(*) > 1
), duplicate_revenue as (
  select revenue_id from source_revenue group by 1 having count(*) > 1
)
select calendar_month, revenue_type, currency from comparison
where e_calendar_month is null or a_calendar_month is null
  or e_transactions is distinct from a_transactions
  or e_gross_revenue_cents is distinct from a_gross_revenue_cents
  or e_refund_amount_cents is distinct from a_refund_amount_cents
  or e_net_revenue_cents is distinct from a_net_revenue_cents
  or e_attributed_net_revenue_cents is distinct from a_attributed_net_revenue_cents
  or e_unattributed_net_revenue_cents is distinct from a_unattributed_net_revenue_cents
  or e_attributed_transactions is distinct from a_attributed_transactions
  or e_unattributed_transactions is distinct from a_unattributed_transactions
  or e_revenue_attribution_rate is distinct from a_revenue_attribution_rate
  or e_purchasing_customers is distinct from a_purchasing_customers
union all
select null, 'duplicate_crosswalk', source_system || ':' || source_identity
from duplicate_crosswalk
union all
select null, 'duplicate_revenue', revenue_id from duplicate_revenue
