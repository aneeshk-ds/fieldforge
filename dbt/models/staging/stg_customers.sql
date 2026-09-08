select
  crm_customer_id,
  first_name,
  last_name,
  normalized_email,
  normalized_phone,
  country,
  cast(created_at as timestamp) as created_at,
  _run_id
from read_parquet('data/silver/customers.parquet')
