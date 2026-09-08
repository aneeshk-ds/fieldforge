# Data model and lineage

```mermaid
erDiagram
  DIM_CUSTOMER |o--o{ FCT_REVENUE : optionally_attributes
  DIM_PLAN ||--o{ MART_SUBSCRIPTION_HEALTH : segments
  DIM_CUSTOMER {
    string customer_sk PK
    string crm_customer_id
    string normalized_email
    string country
  }
  FCT_REVENUE {
    string revenue_id
    string customer_sk "nullable FK"
    date recognized_date
    string revenue_type
    string attribution_status
    bigint gross_amount_cents
    bigint refund_amount_cents
    bigint net_revenue_cents
  }
```

Money uses integer minor units. Revenue remains separated by transaction currency; no invented FX conversion is performed. Every valid financial transaction remains in `fct_revenue`; unresolved identities have a null customer key and `attribution_status = 'unattributed'`. Company revenue includes both attribution states, while customer-level metrics use only attributed rows. The two partitions reconcile exactly at month, revenue type, and currency grain. Customer surrogate keys are deterministic hashes of normalized synthetic email. The identity crosswalk records source identity, canonical key, method, and confidence.
