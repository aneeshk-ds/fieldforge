# Product specification

## Product

FieldForge is a reusable local accelerator for onboarding a subscription-commerce customer. Its reference tenant, Northstar Commerce, supplies imperfect CRM, billing, order, and support extracts. FieldForge produces trusted customer identities, dimensional analytics, governed KPIs, a decision-ready dashboard, and an auditable handover package.

## Users and jobs

- **Customer data owner:** prove that every source row was loaded, accepted, or quarantined.
- **Analytics engineer:** change business rules through versioned SQL, YAML, and tests.
- **Operator:** run and troubleshoot a deterministic pipeline without cloud access.
- **Executive stakeholder:** understand subscriber health, revenue, retention, and fulfillment.
- **Implementation engineer:** map a new customer’s sources and explain trade-offs and exceptions.

## Functional scope

1. Generate reproducible source-shaped synthetic data and planted defects.
2. Profile source quality and publish machine-readable summaries.
3. Ingest immutable bronze Parquet with provenance columns.
4. Validate, standardize, quarantine, and reconcile silver data.
5. Resolve identities across CRM, billing, orders, and support with explainable rules.
6. Build tested customer, subscription, product, order, and KPI models in dbt.
7. Publish governed metrics and a dashboard reading verified gold tables only.
8. Provide CI, container execution, lineage, benchmarking, demo, discovery, and handover assets.

## Non-goals

Real-time streaming, production PII, paid SaaS deployment, probabilistic ML entity resolution, and production-scale distributed compute are intentionally out of scope.

## Personas and success

Success means a reviewer can clone the repository, run one command, inspect planted failures in quarantine, trace a KPI to SQL, reproduce all checks, and explain the implementation in a ten-minute demo.
