select
  source_system,
  source_identity,
  customer_sk,
  match_method,
  cast(confidence as double) as confidence,
  normalized_email
from {{ source('silver', 'identity_crosswalk') }}
