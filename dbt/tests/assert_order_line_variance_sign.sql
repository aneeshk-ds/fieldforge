-- Accepted lines can only be missing, never invented, so an accepted order can
-- never carry more line value than its header amount.
select * from {{ ref('mart_order_line_integrity') }} where line_variance_cents < 0
