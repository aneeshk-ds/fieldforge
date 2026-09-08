# ASTRA Worklog

## 2026-09-08 — Private GitHub publication preparation

- User explicitly authorized private GitHub publication with a maintained progress README.
- README now includes milestone status, prior verification evidence, learning context, release caveats, and next action. Corrected setup prerequisites, dependency-lock wording, and unverified Docker instructions.
- Update README and worklog alongside future milestone commits; public visibility remains a separate release decision.
- Verified GitHub CLI account aneeshk-ds over approved network access. Repository existence check found no aneeshk-ds/fieldforge repository. Generated datasets and local environments are excluded from tracked files; diff whitespace check passed.

## 2026-09-08 — Save and resume checkpoint

- User requested a local commit and pause. All implementation and SQL Lab changes are included; generated data, virtual environments, caches, and database artifacts remain excluded by .gitignore.
- Learning evidence: understood source grain, customer/order IDs, normalization, quarantine, and row reconciliation. Practised SELECT, filtering, aggregation, HAVING, and aliases. Grouping grain and alias placement required correction. Independently wrote the final incoming-count query. Percentage calculation and scalar subqueries required guided steps; do not treat these as independently mastered.
- Teaching preference: project-led learning, short explanations, one practical step at a time. Avoid extended isolated SQL drills. Keep lab exercise text synchronized with teaching.
- SQL Lab: dashboard/sql_lab.py exposes quarantined_orders and incoming_orders with a query editor; exercise 5 remains the guided quarantine-rate calculation. Both tables and subquery execution were verified using Streamlit AppTest. Launch with .venv/bin/streamlit run dashboard/sql_lab.py --server.port 8502.
- Resume next: build a visually polished Data Quality Overview backed by actual layer counts and rejection reasons, then have Aneesh investigate one rejection and verify accounting. Broader visual ambition and measured scale remain part of the product objective.
- Release caveats: prior green checks are limited evidence. Audit revenue excluded by identity matching, source chronology, isolated tests, full dependency locking, Docker workflow, model completeness, and dashboard semantics before release. Spark/Java and Docker execution remain unverified.
- GitHub: user authorized a private aneeshk-ds/fieldforge repository. Browser access was blocked by automatic approval review reporting a usage limit. No remote repository creation or push was completed. Current request is to commit locally and resume later.

## Learner SQL workspace — 2026-09-07

- Added dashboard/sql_lab.py: DuckDB-backed Streamlit query editor with six real synthetic quarantine rows, four readable text columns, and a SELECT-only exercise workspace in memory.
- First exercise: identify unsupported-currency orders and order their IDs. Learner writes the full query; no solution prefilled. Prior SQL tracker consulted for SELECT/WHERE/ORDER BY familiarity; no mastery or gate changes recorded before an attempt.

## Guided learning and visual direction — 2026-09-07

- User requested beginner-first teaching and an ambitious final visual experience and demonstrated scale. Proceed one lesson and learner exercise at a time.
- Visual target: polished onboarding console, quality investigation, identity/lineage exploration, and governed business views. Larger workloads must have measured benchmarks; retain ₹0 constraint.
- Lesson 01 uses actual synthetic order ORD-0000001 and CRM-000475: three PROD-007 items at 1,375 cents, totaling USD 41.25. Interactive journey illustrates arrival, normalization, matching, and metric contribution.
- Source inspection also found the CRM creation timestamp follows this order date; chronology requires a generator/semantics audit in a later implementation slice. The teaching example illustrates matching and arithmetic, not validated lifecycle chronology.
- Prior claims that only runtime checks remain were too broad. Data semantics, excluded-revenue accounting, test isolation, dimensional completeness, and visual QA still require review before release.

This log records implementation decisions, delegated work, verification evidence, errors, and outcomes. Times are in Asia/Kolkata.

## 2026-09-07 — Phase 0

- **Scope:** Initialized an empty repository for the Northstar Commerce onboarding platform.
- **Delegation:** None. Work performed by the primary Astra agent.
- **Decisions:** Local-first DuckDB/Parquet architecture; dbt owns analytical SQL; Python owns generation, contracts, ingestion, identity, orchestration, and reconciliation; PySpark remains optional so the default path is laptop-friendly.
- **Cost decision:** No paid service, API key, cloud account, or proprietary dataset is permitted.
- **Artifacts:** Product specification, requirements, ADRs, acceptance criteria, customer brief, data specification, repository map, initial runbook.
- **Verification:** Pending implementation and clean-environment test.
- **Errors:** None.
- **Outcome:** Phase 0 product contract established; implementation in progress.

## 2026-09-07 — Vertical slices and release verification

- **Delegation:** None. Work performed by the primary Astra agent.
- **Implemented:** Six deterministic source extracts; JSON profiling; provenance-rich bronze Parquet; rule-coded silver/quarantine split; deterministic identity crosswalk; 11 dbt staging/mart models; 14 dbt tests; financial/FK reconciliation; three gold Parquet exports; four-query dashboard smoke gate; Streamlit/Plotly UI; optional PySpark parity slice; Docker/Compose; GitHub Actions; discovery, handover, troubleshooting, benchmark, demo, model, and resume documents.
- **Error:** Initial setup attempted user-level uv cache/runtime paths, rejected by workspace sandbox. **Decision:** make setup now keeps both under the repository and ignores them in Git.
- **Error:** First dbt run resolved profile and Parquet paths from repository root. **Decision:** normalize dbt paths to repository-root-relative paths.
- **Error:** First revenue reconciliation compared all accepted financial rows to facts that deliberately exclude unresolved identities. **Decision:** reconcile the explicitly fact-eligible population by joining the explainable identity crosswalk; unmatched records remain visible in that crosswalk.
- **Verification:** make setup succeeded with Python 3.13 and 83 pinned packages. make all succeeded: dbt PASS=25/WARN=0/ERROR=0; pytest 4 passed; revenue and FK reconciliation all true; dashboard smoke check passed all four queries. Ruff check succeeded with no findings.
- **Environment note:** sandboxed PyArrow emitted non-fatal CPU sysctl warnings; no data or test failures resulted.
- **Verification update:** Final default-scale make all passed after planted-count hardening: 10,163 source rows; exact planted/quarantined counts of 7/4/4/6/4/4 across the six sources; dbt 25/25; pytest 4/4; three reconciliations true; four dashboard queries executable. Warm-cache make pipeline baseline: 42.84 seconds wall time. Ruff remained clean.
- **Pending release checks:** Optional PySpark parity could not run because this host has no Java runtime. Docker build/Compose could not run because Docker is unavailable. CI must execute on GitHub after repository publication. Public repository creation/push was not authorized and was not attempted.
- **Outcome:** Core local implementation and evidence are complete. The overall definition of done remains explicitly open until Spark, Docker, and hosted CI are verified in capable environments.
