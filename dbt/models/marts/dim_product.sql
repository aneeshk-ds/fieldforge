-- Grain: one row per product_id observed on an accepted order line.
-- Northstar Commerce supplies no product master extract, so this dimension is
-- derived from transactional evidence and states the observed price range.
select
  substr(sha256('product|' || product_id), 1, 16) as product_sk,
  product_id,
  min(unit_price_cents) as min_observed_unit_price_cents,
  max(unit_price_cents) as max_observed_unit_price_cents,
  count(distinct unit_price_cents) as observed_price_variants,
  count(*) as observed_order_lines,
  sum(quantity) as observed_units
from {{ ref('stg_order_items') }}
group by product_id
