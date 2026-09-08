# Synthetic data specification

## Seed and scale

Default seed: `20260907`. Default scale: 500 canonical people, 3 plans, 24 products, and twelve months ending 2026-08-31. The generator accepts overrides for seed and customer count.

## Source extracts

| Source | File | Grain | Natural key | Important fields |
|---|---|---|---|---|
| CRM | `customers.csv` | contact | `crm_customer_id` | name, email, phone, country, created_at |
| Billing | `subscriptions.csv` | subscription | `subscription_id` | billing_customer_id, plan, status, dates, monthly price |
| Billing | `invoices.csv` | invoice | `invoice_id` | subscription, paid/refund dates, gross/refund amounts, currency |
| Storefront | `orders.csv` | order | `order_id` | storefront customer, timestamps, status, amount, currency |
| Storefront | `order_items.csv` | order line | order/product/line | quantity, unit price |
| Support | `tickets.csv` | ticket | `ticket_id` | requester email, opened/resolved, category, CSAT |

## Controlled imperfections

`config/planted_errors.yml` is the executable manifest. Defects include malformed emails, duplicate CRM IDs, missing required keys, impossible timestamps, negative quantities, unsupported currencies, amount mismatches, orphan foreign keys, and cross-source identity variants. Planting is deterministic and records retain a `_planted_error` diagnostic column in source fixtures; production validation must not rely on that column.

## Privacy

Faker uses fictional names, reserved `.example` email domains, and synthetic phone numbers. A conspicuous synthetic-data banner appears in generated manifests.
