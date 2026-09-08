select invoice_id, subscription_id, billing_customer_id, cast(paid_at as date) paid_at,
  try_cast(nullif(refunded_at, '') as date) refunded_at,
  cast(gross_amount_cents as bigint) gross_amount_cents,
  cast(refund_amount_cents as bigint) refund_amount_cents, currency
from read_parquet('data/silver/invoices.parquet')
