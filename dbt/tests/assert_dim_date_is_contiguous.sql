select date_key, previous_date_key
from (
  select date_key, lag(date_key) over (order by date_key) as previous_date_key
  from {{ ref('dim_date') }}
)
where previous_date_key is not null and date_diff('day', previous_date_key, date_key) <> 1
