select ticket_id, normalized_email, cast(opened_at as timestamp) opened_at,
  try_cast(nullif(resolved_at, '') as timestamp) resolved_at, category,
  try_cast(nullif(csat, '') as integer) csat
from {{ source('silver', 'tickets') }}
