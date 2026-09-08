select
  date_trunc('month', recognized_date)::date as calendar_month,
  revenue_type,
  currency,
  count(distinct revenue_id) as transactions,
  sum(gross_amount_cents) as gross_revenue_cents,
  sum(refund_amount_cents) as refund_amount_cents,
  sum(net_revenue_cents) as net_revenue_cents,
  coalesce(sum(net_revenue_cents) filter (where attribution_status = 'attributed'), 0) as attributed_net_revenue_cents,
  coalesce(sum(net_revenue_cents) filter (where attribution_status = 'unattributed'), 0) as unattributed_net_revenue_cents,
  count(*) filter (where attribution_status = 'attributed') as attributed_transactions,
  count(*) filter (where attribution_status = 'unattributed') as unattributed_transactions,
  100.0 * sum(net_revenue_cents) filter (where attribution_status = 'attributed')
    / nullif(sum(net_revenue_cents), 0) as revenue_attribution_rate,
  count(distinct customer_sk) as purchasing_customers
from {{ ref('fct_revenue') }}
group by 1,2,3
