# Tools and evidence map

This is an implementation inventory for technical reviewers, not a production deployment claim. FieldForge uses seeded synthetic data for the fictional Northstar Commerce customer. It requires no paid service or cloud account. The worklog records dated verification and distinguishes Aneesh's practice from agent implementation.

The separate [interview-grade practice plan](interview-practice-plan.md) lists every implementation, operations, testing, visualization, and evidence tool in this repository. All rows remain ungraded until Aneesh completes the learner-authored explain/use/diagnose/defend/retain sequence; a working agent-built artifact is not a learner credential.

| Tool or format | Input → output and practical purpose | Code or reproducible evidence |
|---|---|---|
| Python | Source records → pipeline stages, controls and command-line orchestration | [CLI](../fieldforge/cli.py), [independent controls](../fieldforge/reconciliation.py); `make all` |
| NumPy, Faker | Fixed seed and customer count → repeatable synthetic values and identities | [Generator](../fieldforge/generate.py); both direct imports are explicitly locked dependencies |
| pandas | Six CSV extracts → profiles, standardized records, identity crosswalk and quarantine populations | [Pipeline](../fieldforge/pipeline.py), [generation](../fieldforge/generate.py) |
| PyArrow / Parquet | DataFrames and accepted records → typed columnar bronze/silver/gold storage and independent control inputs | [Pipeline](../fieldforge/pipeline.py), [reconciliation](../fieldforge/reconciliation.py) |
| DuckDB / SQL | Accepted Parquet → local analytical warehouse, joins, windows and dashboard aggregates | [dbt models](../dbt/models/), [dashboard queries](../dashboard/queries.py) |
| dbt Core / dbt-duckdb | Source definitions and SQL models → staged tables, dimensions, facts, marts, lineage and failing-row tests | [dbt project](../dbt/dbt_project.yml), [model schema](../dbt/models/schema.yml), [singular tests](../dbt/tests/); `make dbt` |
| Streamlit | Governed warehouse queries and evidence artifacts → dashboard and hands-on SQL Lab | [Dashboard](../dashboard/app.py), [SQL Lab](../dashboard/sql_lab.py); `make dashboard` |
| Plotly | Query results → interactive charts and formatted tooltips | [Business view](../dashboard/app.py); scoped AppTest and browser receipts in the worklog |
| **Apache Spark / PySpark 4.0.0** | Bronze orders and independently accepted silver IDs → Spark-filtered Parquet and missing/unexpected-ID comparison | [Spark job](../spark/standardize_orders.py); `make spark` with the optional `spark` dependency extra |
| **Java 17** | JVM runtime → execution of the optional local Spark job | Recorded Spark run: Java 17.0.20, 1,494 accepted IDs, zero missing/unexpected; `artifacts/spark_parity.json` |
| pytest / Streamlit AppTest | Isolated fixtures, corrupt outputs and actual model/app code → regression and rendering assertions | [Tests](../tests/), [isolated fixture contract](../tests/conftest.py); `make test`; scoped AppTest receipts in worklog |
| Ruff | Python source → lint findings | `.venv/bin/ruff check .`; hosted CI currently checks `fieldforge dashboard tests` |
| uv | `pyproject.toml` plus `uv.lock` → locked Python environment | [Dependencies](../pyproject.toml), [lock](../uv.lock), [setup target](../Makefile); `make setup` |
| Make | Pipeline targets → ordered generation, dbt, exports, release controls and tests | [Makefile](../Makefile); `make all`, `make benchmark` |
| Docker / Compose / Buildx | Dockerfile, locked dependencies and code → Linux image, pipeline service and dashboard service | [Dockerfile](../Dockerfile), [Compose](../compose.yml); full container receipts in worklog |
| Git / GitHub / GitHub Actions | Versioned milestone → hosted lint, full pipeline/tests and uploaded evidence | [CI workflow](../.github/workflows/ci.yml), [worklog](../ASTRA_WORKLOG.md); private `claudework` branch |
| YAML | Versioned definitions → dbt/CI/Compose configuration and human-readable source/KPI contracts | [Configuration](../config/); source/KPI YAML is documentation, not a dynamically loaded Python validation engine |
| CSV / JSON | Source extracts and stage results → reproducible inputs, manifests, profiles, validation, reconciliation and benchmark receipts | [Evidence writers](../fieldforge/utils.py), [benchmark protocol](benchmark.md); generated `data/` and `artifacts/` are Git-ignored |
| Markdown / Mermaid | Architecture and delivery decisions → reviewable documentation and diagrams | [Architecture](architecture.md), [KPI audit](kpi-audit.md), [handover](handover.md) |

## What the evidence does and does not prove

- The standard `make all` gate exercises Python, dbt, exports, reconciliation, Python tests and six dashboard SQL queries. It does not run Spark, Docker builds or browser QA; those have separate dated receipts in [ASTRA_WORKLOG.md](../ASTRA_WORKLOG.md).
- Spark runs with `local[*]`. Its verified slice compares accepted order counts and IDs, not every column, source, or distributed cluster. It uses repository-relative roots rather than the standard relocation environment variables. Java and the optional Spark extra are not included in the default Docker image.
- Docker verification establishes Linux/x86_64 execution under Docker Desktop; native evidence is macOS. Neither proves cloud deployment, high availability or production capacity.
- Benchmarks cover 1× and 10× seeded local workloads. See the protocol for measured duration and scoped memory limitations; this is not a performance SLA.
- Pandera and PyYAML are pinned dependencies but have no application imports/calls. Do not describe them as an executed validation or contract engine. Historical worklog references to Python/Pandera are superseded by this code audit; validation uses custom Python/pandas rules.
- GitHub CLI and an in-app browser were used for delivery and verification. They are development tools, not FieldForge runtime dependencies. Agent-assisted work is attributed explicitly in the worklog; tool availability alone is not implementation evidence.
- Revenue currencies remain separate, unmatched identities are retained, and unresolved source contradictions require investigation. Remaining KPI and operational gaps are tracked in the [audit](kpi-audit.md) and [acceptance criteria](acceptance-criteria.md).
