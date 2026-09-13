# FieldForge

> Verified private portfolio prototype. Public release and any merge to `main` remain unauthorized. Interview-grade learner practice is tracked separately and has not been claimed.

FieldForge is a zero-cost customer data onboarding platform built around a fictional subscription-commerce implementation for **Northstar Commerce**. It turns messy CRM, billing, order, and support extracts into a governed local lakehouse, reconciled KPIs, and a traceable Streamlit dashboard.

## Why this project exists

The repository demonstrates the work expected of a Data Engineer, Analytics Engineer, AI & Data Consultant, or Forward Deployed Engineer: discovery, data contracts, profiling, validation, quarantine, identity resolution, dimensional modelling, KPI governance, delivery automation, and customer handover.

## Tools and technology

| Area | Tools actually used | Inspectable implementation |
|---|---|---|
| Synthetic data | Python, NumPy, Faker, pandas | [Seeded six-source generator](fieldforge/generate.py) |
| Ingestion and quality | pandas, PyArrow, Parquet; custom Python validation | [Profiling, provenance, quarantine and identity rules](fieldforge/pipeline.py) |
| Analytics | SQL, DuckDB, dbt Core, dbt-duckdb | [Declared-grain models and tests](dbt/), [independent Python reconciliation](fieldforge/reconciliation.py) |
| User interface | Streamlit, Plotly | [Operational dashboard](dashboard/app.py), [interactive SQL Lab](dashboard/sql_lab.py) |
| Optional Spark slice | **Apache Spark / PySpark 4.0.0, Java 17** | [Executed local order-ID parity check](spark/standardize_orders.py): 1,494 accepted orders, zero missing or unexpected IDs |
| Tests and automation | pytest, Streamlit AppTest, Ruff, uv, Make | [Tests](tests/), [locked environment](uv.lock), [commands](Makefile) |
| Containers | Docker, Docker Compose, Buildx | [Dockerfile](Dockerfile), [Compose services](compose.yml); native macOS and Linux container gates recorded in the worklog |
| Versioning and CI | Git, GitHub, GitHub Actions | [Hosted quality/evidence workflow](.github/workflows/ci.yml), private milestone history |
| Contracts and evidence | YAML, CSV, JSON, Markdown, Mermaid | [KPI registry](config/kpis.yml), [source contracts](config/), [architecture](docs/architecture.md), generated evidence JSON |

See the [tools and evidence map](docs/tools-and-evidence.md) for inputs, outputs, reproduction commands and limits, and the [complete interview-practice plan](docs/interview-practice-plan.md) for the 38 explicitly ungraded tool/format capabilities. Pandera and PyYAML are declared dependencies but are **not invoked by application code**; validation is implemented in Python/pandas. Automated verification is evidence about the software, not evidence that Aneesh personally mastered a tool.

## System capabilities demonstrated

| Skill | Evidence in the project |
|---|---|
| Customer data onboarding | Six-source discovery, source contracts, provenance, normalization, and no-silent-loss processing |
| Data quality governance | Rule-coded quarantine, record-level evidence, source-owner requests, chronology controls, and reconciliation |
| Identity resolution | Deterministic exact-email crosswalk with unmatched identities retained instead of guessed |
| Dimensional modelling | Customer, plan, product, and date dimensions with revenue and order-line facts at declared grains |
| KPI design | Currency-separated revenue, attribution coverage, subscription health, support health, and order-line integrity |
| Analytical SQL | Joins, window functions, conditional aggregation, grain tests, and traceable dashboard queries |
| Product and consulting delivery | Customer brief, decisions, acceptance criteria, operational UI, demo path, troubleshooting, and handover documentation |

## Progress — updated 13 September 2026

**Current stage:** The private implementation, KPI audit, operational hardening, native/container/Spark gates, and portfolio documentation are complete. **Remaining authority-dependent work:** no public release or merge to `main`. **Deferred learner work:** resume the interview-grade practice plan one tool at a time when Aneesh requests it.

| Milestone | Status | Evidence / next action |
|---|---|---|
| Customer brief, specification, architecture | Complete for private prototype | Versioned documents in docs/ |
| Synthetic sources, profiling, bronze/silver/quarantine | Verified | 10,163 generated rows across six sources; 29 quarantined with no silent loss |
| Identity resolution and analytical models | Dimensional coverage complete | 18 dbt models; every source modelled; grains declared on every model; unattributed revenue retained |
| Automated quality checks | Native and rebuilt-container checks passed; tests isolated and dependencies locked | 122 dbt tests, 109 Python tests, 20 reconciliation controls, 7 dashboard query checks; `uv.lock` resolves the complete environment |
| Dashboard and SQL Lab | Verified command center; lab paused | Four source-backed views with governed churn, revenue coverage, source-aware investigation, and complete order-line population; SQL Lab is optional for later genuine practice |
| Data Quality Overview and visual design | Implemented; locally verified | Source controls, rejection diagnostics, record drill-down, and governance traceability |
| Larger-scale benchmarks | Reproducible local evidence published | 10× processed 102,479 rows; cold 130.938 s and warm 155.108 s; single-host evidence, not a capacity claim |
| Docker, Spark parity, hosted CI | Verified | PySpark matched all 1,494 accepted order IDs on Java 17; rebuilt Linux/x86_64 image and Compose service passed the full isolated gate; final milestone hosted CI passed |
| Interview-grade learner practice | Explicitly ungraded and deferred | 38 tools/formats have explain/use/diagnose/defend/retain requirements in the practice plan |
| Public portfolio release | Not authorized | Requires explicit approval; `main` remains untouched |

### Latest project session

**Aneesh did:** Corrected the order-line business population to 3,021 after clarification; this is recorded as a KPI-population decision, not tool mastery. Aneesh then explicitly paused learning checkpoints until the product is finished and required a complete interview-grade tool plan for later. **Agent implemented:** Added direct-source Python and dbt order controls, corruption coverage, full accepted-line dashboard totals, exact labels, transient DuckDB-lock handling, truthful dependency declarations, acceptance/presentation updates, and the 38-item grading contract. The dashboard now derives a private software/portfolio progress bar from the acceptance checklist: 14/14, 100%, while keeping learner grading explicitly separate at 0/38. **Verification:** Native macOS and rebuilt Linux/x86_64 gates passed 140 dbt nodes, 20 controls, 109 Python tests, four exports, seven dashboard queries and Ruff; Compose and disposable clean-clone gates passed before the two progress-specific tests were added. Spark again matched all 1,494 accepted orders on Java 17. All source hashes are unchanged. Browser rehearsal covered quality triage, order integrity, business health, lineage, and the progress bar on native and Docker dashboards. [GitHub Actions run 34760584794](https://github.com/aneeshk-ds/fieldforge/actions/runs/34760584794) passed the preceding final-acceptance milestone; the branch-tip workflow status remains authoritative for later commits.

### Previous session

Completed the independent full-series logo-churn control using accepted Parquet and Python calendar arithmetic, building on Aneesh's already-completed 4 / 84 = 4.76% exercise. All 60 month/plan groups reconcile; source files and previous subscription values are unchanged. Added 17 corruption/boundary tests and a dbt source comparison. Native and rebuilt Docker gates passed 126 dbt nodes, 18 controls, 74 Python tests and six dashboard queries. The [tools and evidence map](docs/tools-and-evidence.md) now makes Spark/Java and every implemented tool inspectable, correcting unused Pandera claims. This completes the reconciliation/documentation chunk; churn presentation remains a learner checkpoint, followed by revenue/order KPI review and operational acceptance.

### Previous session

Audited average satisfaction after Aneesh correctly calculated 3.5 from ratings 2 and 5 and identified an out-of-range 5.9 input as requiring investigation. Fixed validation to quarantine invalid ratings without rounding; registered the mean out of 5, exposed its rated-ticket denominator, added independent checks, and made rating count/mean visible in the existing support tooltip. Native and rebuilt Docker gates passed 125 dbt nodes, 17 controls, 57 Python tests and six dashboard queries. AppTest checked all 48 tooltip groups on both platforms; original source data and previous support values are unchanged. Next: finish the independent logo-churn reconciliation and remaining [KPI audit](docs/kpi-audit.md), preserving the learning checkpoints.

### Previous session

Audited average resolution time through Aneesh's correction that an unresolved ticket has an unknown completed duration, not zero. The two-ticket teaching example therefore averages 40 hours over one completed ticket. Registered the opening-month/category definition, exposed the completed-ticket denominator, replaced hour-boundary counting with continuous elapsed hours, and added independent reconciliation plus zero/unknown/fractional-time tests. All 48 existing support groups retain their previous values; the new denominator totals 460 resolved tickets out of 496 accepted. Native SSD `make all` passed 123 dbt nodes, 16 controls, 31 Python tests and six dashboard queries. Scoped native browser verification confirmed the completed-count and hours tooltip. Rebuilt Docker images also passed the full gate and Ruff on Linux/x86_64 (Python 3.13.15); the Docker dashboard health, support rendering and warehouse values were checked. The build now excludes the host `.uv-python` installation. Next: average satisfaction rating, then the remaining [KPI audit](docs/kpi-audit.md); no portfolio polish yet.

### Previous session

Audited accepted support tickets opened by month and category. Aneesh correctly assigned real ticket `TKT-000459` to September 2025 despite its October resolution. The existing count was correct: 12 accepted account tickets opened in September. Added the missing KPI definition, an accepted-source dbt reconciliation test, an independent Python release control, and explicit opening-month/count labels and caveats. Native SSD `make all` passed 121 dbt nodes, 15 reconciliation controls, 23 Python tests, and six dashboard queries. The scoped live chart check passed, and hosted CI passed for implementation commit `d740263` (run 34614611134, confirmed 12 September). Next: average resolution hours, one learner checkpoint at a time; the [working KPI audit](docs/kpi-audit.md) tracks outstanding coverage and findings.

### Previous session

Audited the active-subscriber month-end boundary using real subscription `SUB-000254`. Aneesh determined that a subscription cancelled on the month-end date remains active for that snapshot and corrected the SQL comparison from `>` to `>=`. Premium March 2026 therefore reconciles at 88 rather than 87. The registry, dbt mart, new dbt reconciliation test, and release reconciliation control now agree; the broader KPI audit remains open.

### Previous session

Installed Docker Desktop with its Linux disk image on the external SSD, keeping the capacity-heavy container store separate from the Mac's constrained internal drive. Aneesh corrected the dependency command to `uv sync --locked --extra dev` after the first container run proved that excluding development tools also excluded `pytest`, which `make all` requires. Both Compose images then built successfully, and the Linux/x86_64 `fieldforge` container passed all 119 dbt nodes, four gold exports, 13 reconciliation controls, 15 Python tests, and six dashboard SQL checks.

### Earlier session

Locked the complete dependency graph with uv after a learner checkpoint distinguished FieldForge's 10 declared direct dependencies from the 85 distributions installed in the working environment. The cross-platform lock resolves 87 packages, including optional environments, and both `make setup` and the Docker image now enforce it with `--locked`. A disposable clean-copy verification proves setup and the full pipeline do not depend on the existing `.venv`, generated data, artifacts, or caches.

### Earlier session

Verified the optional PySpark 4.0.0 order-standardization slice on macOS with Java 17. The job matched the canonical pipeline's 1,494 accepted orders with zero missing or unexpected IDs and now writes durable `artifacts/spark_parity.json` evidence without collecting identifiers into pandas. The Make target binds Spark to FieldForge's Python interpreter, fixing its accidental use of system Python 3.14. Docker is not installed on this host, so execution remains honestly blocked; static inspection found and fixed the image's missing `make` dependency because Compose invokes `make all`.

### Earlier session

Added an isolated benchmark workflow after Aneesh selected the 10× / 5,000-customer profile from the real 500-customer baseline. `make benchmark` refuses the demo roots, records stage timings, row counts, environment, dbt coverage, scoped memory evidence, and archives the prior observation. The measured 10× workload contains 102,479 rows versus 10,163 at 1×; it passed all 119 dbt nodes, 13 reconciliations, and six dashboard checks in both cold and warm observations. The SQL Lab now displays the two latest profiles, while [the benchmark protocol](docs/benchmark.md) records the exact environment, results, and claim boundary.

### Earlier session

Surfaced `mart_order_line_integrity` as a dedicated dashboard view after a learner decision to emphasize the known quarantined-line consequence. The primary callout traces `ORD-0000015` to one retained quarantined line and its USD 90.00 variance; the two unexplained cases remain visible as a secondary source-owner backlog. The dashboard query returns all 1,494 accepted orders at declared order grain, and a Python test pins the three incomplete orders and their evidence status. Repository-owned Streamlit calls now use the supported `width` argument, and live browser QA verified the hierarchy and values.

### Earlier session

Corrected the seeded customer lifecycle chronology after a learner checkpoint established that event timestamps are evidence and the later CRM first-seen value is wrong. The generator now derives each event-bearing customer's `created_at` on or before their earliest subscription, order, or support event; customers without events retain their independent seeded date. A dbt singular test and release reconciliation control both require zero violations, and the SQL Lab exposes the actual one-row-per-customer chronology preview. The SSD `make all` run passed with 101 dbt tests, 13 Python tests, 13 reconciliation controls, and five dashboard checks. Revenue, quarantine, and order-line integrity figures did not move.

### Earlier session

Isolated test outputs from the demo run. `FIELDFORGE_DATA_ROOT` and `FIELDFORGE_ARTIFACTS_ROOT` now decide where a run lands, resolved when a path is used rather than at import, and `dbt/profiles.yml` and `sources.yml` read the same variable through `env_var` with a `data` default. Tests point it at a temporary directory, so `pytest` no longer rewrites source records, evidence artifacts, or the run ID the dashboard reports. Evidence from a passing test run is disposable; a failing run copies its evidence JSON and a failure report to the Git-ignored `artifacts/test-runs/<run-id>/`. A complete run against a separate root also passes, dbt included, which makes parallel and benchmark runs possible without disturbing demo data.

### Dimensional modelling session

Closed the dimensional gap. `order_items` was generated, validated, and quarantined but never modelled; it now flows through `stg_order_items` into `fct_order_item` at order-line grain, joined to a derived `dim_product` and a data-driven `dim_date`. Every model declares its grain, staging models read governed dbt sources instead of raw file paths, and `mart_order_line_integrity` publishes the consequence of quarantining a line: **3 of 1,494 accepted orders** no longer reconcile to their line totals, and **8 of 3,021 accepted lines** belong to a quarantined order and are retained with `order_link_status = 'order_not_accepted'` rather than dropped. Prior marts are unchanged: 5,646 revenue transactions and 31,597,300 net cents, with monthly KPI, subscription, and support outputs identical to the previous run.

### How progress stays current

At each completed project milestone, update this section's date, status, evidence, and next action in the same commit as the work. Append detailed decisions and verification to [ASTRA_WORKLOG.md](ASTRA_WORKLOG.md). This is a maintained progress record, not an automatic percentage-complete estimate.

### Before calling this complete

- [x] Account for financial records excluded by unresolved identities.
- [x] Complete dimensional models with declared grains and key tests.
- [x] Isolate test data so tests never replace the demo run.
- [x] Lock the full dependency environment.
- [x] Correct synthetic customer chronology and enforce it in dbt and reconciliation.
- [x] Audit remaining KPI semantics and independent reconciliation.
- [x] Validate dashboard values and visuals against the completed models.
- [x] Verify PySpark parity on Java 17.
- [x] Verify Docker and clean-clone setup.
- [x] Keep hosted CI green for the latest milestone.
- [x] Publish reproducible local scale benchmarks with explicit claim boundaries.
- [x] Finish customer handover for the known quarantined-line case with a learner-authored operator action.

Learning remains required before claiming personal tool proficiency, but Aneesh explicitly deferred it so the private software and portfolio pipeline could be completed first. No prior arithmetic, approval, observation, or display choice is counted as tool mastery. The exact 38-item grading contract lives in [the interview-practice plan](docs/interview-practice-plan.md) and resumes only when Aneesh requests it.

If another coding agent must continue this exact local project, start with [CLAUDE.md](CLAUDE.md), then read this README and [ASTRA_WORKLOG.md](ASTRA_WORKLOG.md).

## Quick start

Requirements: `uv`, `make`, and internet access for initial dependency downloads. Setup provisions Python 3.13 locally. No cloud account, secrets, or paid API is required.

```bash
make setup
make all
make dashboard
```

Optional SQL practice workspace after running the pipeline (do not launch unless it supports an active learner-authored exercise):

```bash
.venv/bin/streamlit run dashboard/sql_lab.py --server.port 8502
```

Source generation is seeded. Outputs are written to `data/` and `artifacts/`, both ignored by Git. Docker/Compose builds and the full container pipeline are verified on Docker Desktop 4.90.0 with Engine 29.7.2 using Linux/x86_64 containers.

## Commands

| Command | Purpose |
|---|---|
| `make setup` | Create `.venv` and install the locked project plus development dependencies |
| `make pipeline` | Generate → profile → bronze → silver → gold → reconcile |
| `make test` | Python tests and dashboard query smoke check |
| `make all` | Run the pipeline and all tests |
| `make dashboard` | Start the Streamlit KPI application |
| `make spark` | Run the optional PySpark order parity check (requires the `spark` extra and Java 17) |
| `make benchmark` | Run the isolated 10× profile and record reproducible evidence |
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
