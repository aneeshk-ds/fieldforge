# FieldForge continuation guide

This file is the continuity contract for any development agent. Work only in the canonical repository at `/Volumes/AK-SSD-MAC/Codex Work/FieldForge`; never use or recreate the stale internal copy.

## Repository and release boundary

- Private remote: `https://github.com/aneeshk-ds/fieldforge`
- Default and active delivery branch: `production-preview`
- `main`, public visibility, and deployment require Aneesh's explicit authorization.
- Product: a zero-cost customer-data onboarding reference platform for fictional Northstar Commerce.
- Runtime rule: no paid API, secret, cloud billing, proprietary warehouse, or real customer data.

Before changing anything, read `README.md`, the newest `ASTRA_WORKLOG.md` entries, `docs/kpi-audit.md`, `docs/tools-and-evidence.md`, and `docs/acceptance-criteria.md`. Then inspect branch, status, recent commits, origin synchronization, generated evidence, processes, ports, and Docker workloads. Preserve unrelated work.

## Current execution policy

Aneesh explicitly canceled the repository's teaching/checkpoint workflow. Do not create exercises, grade personal knowledge, or block delivery on learner attempts. The SQL surface is an operational read-only workbench. Optimize for a complete, inspectable, résumé-ready implementation and honest evidence.

Historical attribution remains in `ASTRA_WORKLOG.md`. New worklog entries must distinguish exactly:

- **Aneesh did**
- **Agent implemented**
- **Verification**

## Current product state

- Six deterministic synthetic CRM, subscription, invoice, order, order-item, and support extracts.
- PyYAML-loaded, Pandera-enforced ordered source schemas before bronze ingestion.
- Bronze/silver/gold Parquet layers, DuckDB warehouse, and explicit rule-coded quarantine.
- Exact normalized-email identity crosswalk; unresolved valid identities remain unattributed and are never guessed.
- 18 dbt models, declared grains, data tests, independent controls, four gold exports, and seven dashboard SQL checks.
- Streamlit/Plotly command center, order-integrity view, exception investigation, and read-only DuckDB SQL workbench.
- Docker/Compose/Buildx, GitHub Actions, optional Java 17/PySpark parity, isolated benchmarks, and versioned operational documentation.
- Executable `portfolio-check` validates the 39-tool inventory, evidence paths, essential reviewer documents, and stale active-state claims.

The repository is a verified private portfolio implementation, not a publicly hosted production service. Keep scope claims explicit.

## Supported commands

```bash
make setup            # locked default and development environment
make setup-all        # default, development, and Spark dependencies
make pipeline         # generation through gold exports and reconciliation
make test             # Python tests and dashboard SQL checks
make all              # supported pipeline and test gate
make portfolio-check  # 39-tool and reviewer-evidence contract
make verify           # all + portfolio check + full Ruff + Spark parity
make dashboard        # command center on localhost:8501
.venv/bin/streamlit run dashboard/sql_lab.py --server.port 8502
```

Use both `FIELDFORGE_DATA_ROOT` and `FIELDFORGE_ARTIFACTS_ROOT` for isolated runs. Never let a verification run overwrite the preserved demo data. Inspect Docker workloads before stopping or changing any container resources.

## Governed decisions

1. Invalid records are quarantined with provenance and reasons, never silently discarded.
2. Structural schema drift fails before bronze; business-rule failures enter quarantine after bronze.
3. Supported currencies are USD, CAD, and GBP and must not be summed without an approved FX model.
4. Company revenue includes valid unattributed transactions; customer metrics use attributed revenue only.
5. Unresolved identity is never guessed. Attributed rows require a valid customer key; unattributed rows require a null key.
6. Orders are one row per order. All 3,021 accepted lines are retained: 3,013 link to accepted headers and eight remain without one.
7. Header-to-line mismatches remain visible: one known quarantine impact and two unexplained source-owner investigations.
8. Active subscribers use inclusive month-end boundaries; logo churn divides cancellations by prior month-end active subscriptions.
9. Support tickets belong to opening month; unresolved tickets have unknown completed duration, not zero duration.
10. `created_at` must not be later than a customer's first subscription, order, or support event.

## High-risk continuity notes

- Path functions resolve at call time from `FIELDFORGE_DATA_ROOT` and `FIELDFORGE_ARTIFACTS_ROOT`; Python, dbt, dashboards, and Spark must receive the same roots.
- Tests requesting `isolated_data_root` do not touch demo data. Any new mutating test must request it.
- The macOS `.venv` is host-specific; containers create their own Linux environment.
- Spark is an accepted-order-ID parity slice, not full-pipeline or distributed-production proof.
- Generated `data/` and `artifacts/` are Git-ignored evidence, not source-controlled fixtures.
- Historical worklog text is an audit trail and may describe superseded states; current active truth lives here and in the newest receipt.

## Delivery discipline

Inspect the complete diff. Run focused checks first. For runtime changes, run the full native gate and rebuilt isolated Docker gate sequentially, then compare all six source hashes. Run `make verify` when Java/Spark is available. Refresh screenshots only from verified rendered output. Update `README.md`, `ASTRA_WORKLOG.md`, `docs/kpi-audit.md`, this file, and acceptance evidence when continuity changes.

Commit and push meaningful verified milestones only to `production-preview`. Confirm hosted GitHub Actions after the push. Never merge or push to `main` without explicit authorization.

Before stopping, report the final SHA, local/remote synchronization, exact checks, source hashes, CI runs, running processes, Docker state, and any honest limitation.
