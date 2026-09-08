select order_id, storefront_customer_id, normalized_email, cast(ordered_at as timestamp) ordered_at,
  try_cast(nullif(delivered_at, '') as timestamp) delivered_at, status,
  cast(order_amount_cents as bigint) order_amount_cents,
  cast(refund_amount_cents as bigint) refund_amount_cents, currency
from {{ source('silver', 'orders') }}
