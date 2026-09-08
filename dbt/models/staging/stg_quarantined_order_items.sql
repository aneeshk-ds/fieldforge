select
  order_id,
  cast(line_number as integer) as line_number,
  product_id,
  cast(quantity as bigint) as quantity,
  cast(unit_price_cents as bigint) as unit_price_cents,
  _rule_codes,
  _rejection_reasons,
  _raw_key,
  _run_id
from {{ source('quarantine', 'order_items') }}
