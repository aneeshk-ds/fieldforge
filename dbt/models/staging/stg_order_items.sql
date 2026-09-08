select
  order_id,
  cast(line_number as integer) as line_number,
  product_id,
  cast(quantity as bigint) as quantity,
  cast(unit_price_cents as bigint) as unit_price_cents,
  cast(quantity as bigint) * cast(unit_price_cents as bigint) as extended_amount_cents,
  _run_id
from {{ source('silver', 'order_items') }}
