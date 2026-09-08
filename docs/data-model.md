# Data model and lineage

```mermaid
erDiagram
  DIM_CUSTOMER ||--o{ FCT_REVENUE : earns
  DIM_PLAN ||--o{ MART_SUBSCRIPTION_HEALTH : segments
  DIM_CUSTOMER {
    string customer_sk PK
    string crm_customer_id
    string normalized_email
    string country
  }
  FCT_REVENUE {
    string revenue_id
    string customer_sk FK
    date recognized_date
    string revenue_type
    bigint gross_amount_cents
    bigint refund_amount_cents
    bigint net_revenue_cents
  }
```

Money uses integer minor units. Revenue remains separated by transaction currency; no invented FX conversion is performed. Customer surrogate keys are deterministic hashes of normalized synthetic email. The identity crosswalk records source identity, canonical key, method, and confidence.
