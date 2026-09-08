select * from (values
  ('ESSENTIALS', 'Essentials', 2900),
  ('PLUS', 'Plus', 4900),
  ('PREMIUM', 'Premium', 7900)
) as plans(plan_code, plan_name, list_price_cents)
