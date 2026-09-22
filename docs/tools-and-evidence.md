# Tools and evidence map

FieldForge uses every tool it claims. The executable source of truth is [`config/tool_inventory.yml`](../config/tool_inventory.yml); `make portfolio-check` loads it with PyYAML, validates it with Pandera, confirms all 39 IDs and evidence paths, checks required reviewer documents, and writes `artifacts/portfolio_check.json`.

| Layer | Executed tools | Repository evidence |
|---|---|---|
| Source contracts | PyYAML, Pandera, pandas | [`fieldforge/contracts.py`](../fieldforge/contracts.py), [`config/source_contracts.yml`](../config/source_contracts.yml), contract drift tests |
| Generation | Python 3.13, NumPy, Faker, CSV | [`fieldforge/generate.py`](../fieldforge/generate.py), deterministic source hashes |
| Storage and controls | PyArrow, Parquet, JSON | [`fieldforge/pipeline.py`](../fieldforge/pipeline.py), [`fieldforge/reconciliation.py`](../fieldforge/reconciliation.py), generated receipts |
| Analytics | SQL, DuckDB, dbt Core, dbt-duckdb, Jinja | [`dbt/`](../dbt/), 18 models, declared grains, tests, marts, lineage |
| Product | Streamlit, Plotly | [`dashboard/app.py`](../dashboard/app.py), [`dashboard/sql_lab.py`](../dashboard/sql_lab.py), rendered screenshot and AppTest |
| Quality and security | pytest, Streamlit AppTest, Ruff, Gitleaks | [`tests/`](../tests/), full-tree Ruff, corruption/boundary/UI tests, full-history credential scanning in CI |
| Packaging | `pyproject.toml`, Hatchling, uv, `uv.lock`, TOML, Make | [`pyproject.toml`](../pyproject.toml), [`uv.lock`](../uv.lock), [`Makefile`](../Makefile) |
| Runtime parity | Apache Spark, PySpark 4.0.0, Java 17 | [`spark/standardize_orders.py`](../spark/standardize_orders.py), `artifacts/spark_parity.json` |
| Containers | Docker Engine/Desktop, Dockerfile, Compose, Buildx | [`Dockerfile`](../Dockerfile), [`compose.yml`](../compose.yml), hosted container job |
| Delivery | Shell, Git, GitHub, GitHub CLI, GitHub Actions | [CI workflow](../.github/workflows/ci.yml), repository history, hosted run receipts |
| Communication | YAML, Markdown, Mermaid | [`config/`](../config/), [architecture](architecture.md), [reviewer knowledge map](repository-knowledge.md) |

## Proof boundaries

- `make all` proves generation, structural contracts, validation/quarantine, dbt, exports, independent controls, Python tests, and dashboard SQL checks.
- `make verify` additionally proves the 39-tool evidence contract, full-tree Ruff, and the local Java/PySpark parity slice.
- Gitleaks v8.30.1 scans the complete Git history with redacted output locally and before the hosted quality gate.
- Hosted CI runs the quality gate and an isolated rebuilt container gate. It is clean-run evidence, not proof of cloud-scale operations.
- Docker proves Linux package/runtime parity. Native evidence is macOS. Neither claim implies high availability, concurrency, or production capacity.
- Spark honors the relocated data/artifact roots and compares all accepted order IDs locally. It does not claim a distributed cluster or full-pipeline Spark implementation.
- Benchmarks are reproducible 1× and 10× local observations, not an SLA.
- GitHub CLI and browser inspection support delivery verification; they are development tools, not runtime dependencies.
- Revenue stays separated by USD, CAD, and GBP. Unmatched identities remain explicit. Unresolved source contradictions remain open until the source owner supplies evidence.

Use [`docs/repository-knowledge.md`](repository-knowledge.md) to understand component ownership, grains, invariants, failure modes, and the fastest reviewer path.
