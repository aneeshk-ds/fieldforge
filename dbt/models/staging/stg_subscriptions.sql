select
  subscription_id,
  billing_customer_id,
  normalized_email,
  plan_code,
  status,
  cast(start_date as date) as start_date,
  try_cast(nullif(cancelled_at, '') as date) as cancelled_at,
  cast(monthly_price_cents as bigint) as monthly_price_cents,
  currency
from read_parquet('data/silver/subscriptions.parquet')
