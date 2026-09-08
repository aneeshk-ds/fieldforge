# FieldForge

> Work in progress: this is a learning and implementation checkpoint, not a verified release. See ASTRA_WORKLOG.md for remaining work and the resume point.

FieldForge is a zero-cost customer data onboarding platform built around a fictional subscription-commerce implementation for **Northstar Commerce**. It turns messy CRM, billing, order, and support extracts into a governed local lakehouse, reconciled KPIs, and a traceable Streamlit dashboard.

## Why this project exists

The repository demonstrates the work expected of a Data Engineer, Analytics Engineer, AI & Data Consultant, or Forward Deployed Engineer: discovery, data contracts, profiling, validation, quarantine, identity resolution, dimensional modelling, KPI governance, delivery automation, and customer handover.

## Progress — updated 8 September 2026

**Current stage:** working local prototype and guided project learning. **Next milestone:** a polished Data Quality Overview showing received, accepted, and quarantined records, with rejection drill-downs.

| Milestone | Status | Evidence / next action |
|---|---|---|
| Customer brief, specification, architecture | Drafted | Versioned documents in docs/ |
| Synthetic sources, profiling, bronze/silver/quarantine | Implemented; initial local checks passed | 10,163 generated rows across six sources; 29 quarantined |
| Identity resolution and analytical models | Prototype | 11 dbt models; audit unmatched revenue and dimensional completeness |
| Automated quality checks | Initial local checks passed | 14 dbt tests, 4 Python tests; stronger independent controls still needed |
| Dashboard and SQL Lab | Prototype | Four dashboard queries checked; interactive SQL Lab supports two order tables |
| Data Quality Overview and visual design | Next | Build an operational view, then verify it together |
| Larger-scale benchmarks | Pending | Initial warm local pipeline baseline: 42.84 seconds; no scale claim yet |
| Docker, Spark parity, hosted CI | Unverified | Definitions exist; execute and resolve failures before release |
| Public portfolio release | Pending | Complete acceptance criteria and approve public visibility |

### Latest project session

Traced a customer order through normalization, identity matching, quarantine, and reporting. Queried actual order data: **1,500 incoming = 1,494 accepted + 6 quarantined (0.4%)**. Practised counts, grouping, filters, and aliases; scalar subqueries were guided and need reinforcement through project work.

### How progress stays current

At each completed project milestone, update this section's date, status, evidence, and next action in the same commit as the work. Append detailed decisions and verification to [ASTRA_WORKLOG.md](ASTRA_WORKLOG.md). This is a maintained progress record, not an automatic percentage-complete estimate.

### Before calling this complete

- [ ] Account for financial records excluded by unresolved identities.
- [ ] Audit synthetic chronology, KPI semantics, and independent reconciliation.
- [ ] Isolate test data and lock the full dependency environment.
- [ ] Complete dimensional models and validate dashboard values and visuals.
- [ ] Verify Docker, Spark parity, clean-clone setup, and GitHub CI.
- [ ] Publish reproducible scale benchmarks and finish customer handover.

Learning follows project milestones: explain the concept, make a useful change, operate it, and verify the outcome. SQL practice supports delivery.

## Quick start

Requirements: `uv`, `make`, and internet access for initial dependency downloads. Setup provisions Python 3.13 locally. No cloud account, secrets, or paid API is required.

```bash
make setup
make all
make dashboard
```

SQL practice workspace after running the pipeline:

```bash
.venv/bin/streamlit run dashboard/sql_lab.py --server.port 8502
```

Source generation is seeded. Outputs are written to `data/` and `artifacts/`, both ignored by Git. Docker/Compose files are experimental and still require workflow verification.

## Commands

| Command | Purpose |
|---|---|
| `make setup` | Create `.venv` and install pinned direct dependencies (full lock pending) |
| `make pipeline` | Generate → profile → bronze → silver → gold → reconcile |
| `make test` | Python tests and dashboard query smoke check |
| `make all` | Run the pipeline and all tests |
| `make dashboard` | Start the Streamlit KPI application |
| `make spark` | Run the selected optional PySpark equivalent |
| `make benchmark` | Record local pipeline timings |
| `make clean` | Remove only generated local outputs |

## Architecture

```mermaid
flowchart LR
  G[Synthetic source extracts] --> P[Profile + contracts]
  P --> B[(Bronze Parquet)]
  B --> V{Validate and standardize}
  V -->|valid| S[(Silver Parquet)]
  V -->|invalid + reason| Q[(Quarantine)]
  S --> I[Identity resolution]
  I --> D[dbt dimensional models]
  D --> K[(Gold DuckDB + Parquet)]
  K --> R[Reconciliation tests]
  K --> UI[Streamlit + Plotly]
```

See [architecture.md](docs/architecture.md), [data-model.md](docs/data-model.md), and [demo.md](docs/demo.md).

## Repository map

```text
fieldforge/          Python pipeline and shared business rules
dbt/                 DuckDB staging, dimensions, facts, marts, and tests
dashboard/           Streamlit application backed only by verified gold models
spark/               Selected local PySpark transformations
tests/               Contract, quarantine, identity, and reconciliation tests
docs/                Discovery, decisions, diagrams, runbook, and handover
config/              Source contracts and governed KPI definitions
.github/workflows/   Reproducible CI
```

## Definition of done

`make all` exercises the current automated checks; passing it alone does not prove the full release criteria. See [acceptance-criteria.md](docs/acceptance-criteria.md) and the remaining work above. Completion requires current evidence for the entire checklist.

## Data safety

All people, companies, emails, transactions, and tickets are synthetic. The generator plants documented defects deliberately; see `config/planted_errors.yml`. Never use this project’s records as real customer data.

## Portfolio highlights

- Reproducible medallion lakehouse on DuckDB and Parquet with no managed-service dependency.
- Explainable customer identity resolution with durable crosswalks and confidence tiers.
- No-silent-loss validation: every rejected row carries source, rule, reason, and ingest metadata.
- Governed subscription-commerce KPIs with reconciliation tests and SQL-level dashboard traceability.

License: MIT.
