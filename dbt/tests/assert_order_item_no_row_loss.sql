select fact_rows, accepted_rows
from (
  select
    (select count(*) from {{ ref('fct_order_item') }}) as fact_rows,
    (select count(*) from {{ ref('stg_order_items') }}) as accepted_rows
)
where fact_rows <> accepted_rows
