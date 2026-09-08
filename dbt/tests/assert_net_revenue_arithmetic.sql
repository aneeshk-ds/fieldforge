select * from {{ ref('fct_revenue') }}
where net_revenue_cents <> gross_amount_cents - refund_amount_cents
