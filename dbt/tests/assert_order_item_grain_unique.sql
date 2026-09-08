select order_id, line_number, count(*) as rows_at_grain
from {{ ref('fct_order_item') }}
group by order_id, line_number
having count(*) > 1
