select *
from {{ ref('fct_revenue') }}
where (attribution_status = 'attributed' and customer_sk is null)
   or (attribution_status = 'unattributed' and customer_sk is not null)
