-- Grain: one row per accepted canonical CRM customer (customer_sk).
select
  substr(sha256('customer|' || normalized_email), 1, 16) as customer_sk,
  crm_customer_id,
  first_name,
  last_name,
  normalized_email,
  normalized_phone,
  country,
  created_at
from {{ ref('stg_customers') }}
