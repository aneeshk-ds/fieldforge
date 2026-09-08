select
  date_trunc('month', recognized_date)::date as calendar_month,
  revenue_type,
  currency,
  count(distinct revenue_id) as transactions,
  sum(gross_amount_cents) as gross_revenue_cents,
  sum(refund_amount_cents) as refund_amount_cents,
  sum(net_revenue_cents) as net_revenue_cents,
  count(distinct customer_sk) as purchasing_customers
from {{ ref('fct_revenue') }}
group by 1,2,3
