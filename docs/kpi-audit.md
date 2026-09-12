# KPI audit and working gap assessment

Updated 12 September 2026. This is a partial, evidence-based working assessment, not release acceptance. Proceed one KPI and one learner checkpoint at a time; do not begin portfolio screenshots or polish while the audit remains open.

## Accepted support tickets opened — verified slice

- **Source meaning and population:** `fieldforge/generate.py` supplies opening/resolution timestamps and category. `fieldforge/pipeline.py` quarantines contradictory dates and invalid satisfaction scores. The current run has 500 incoming tickets, 496 accepted and four quarantined (`artifacts/validation_summary.json`). The count therefore represents accepted demand; even a ticket rejected only for its satisfaction score is excluded. No customer-identity join is used.
- **Registry and grain:** `config/kpis.yml` defines `support_tickets_opened` at opening calendar month plus category. Both resolved and unresolved accepted tickets count. Source timestamps lack timezone information; use the supplied calendar date without conversion. Empty groups have no row, not a published zero.
- **Transformation:** `dbt/models/staging/stg_tickets.sql` retains ticket identity, opening time and category. `dbt/models/marts/mart_support_health.sql` groups by opening month/category and counts all accepted rows. No calculation change was needed.
- **dbt checks:** `schema.yml` checks ticket identity and non-null mart keys/counts; `assert_support_health_grain_unique.sql` enforces one group row; `assert_support_ticket_counts_reconcile.sql` compares the mart with silver records, bypassing staging.
- **Independent release control:** `fieldforge/reconciliation.py` reads accepted Parquet with PyArrow and uses Python calendar dates and a Counter, independently of dbt SQL. `fieldforge/cli.py` blocks release on any group mismatch. All 48 groups reconcile to 496 accepted tickets. Tests cover a correct result, redistribution with unchanged total, missing/extra/duplicate groups, null count, missing mart rows, and empty source/mart.
- **Query and display:** `dashboard/queries.py` preserves month/category/count. `dashboard/app.py` labels the axes Opening month and Accepted tickets opened, formats whole-ticket values, and explains unresolved/quarantined/empty-group handling. Live native browser inspection verified labels, caption, whole-number axis and tooltip; March 2026 billing showed 18, matching a direct database query. This is scoped chart verification, not complete dashboard QA.
- **Learner evidence:** Aneesh assigned `TKT-000459` (opened 30 September, resolved 2 October 2025) to September because that is its initiation period. Read-only inspection confirms it belongs to September/account's count of 12. Agent implemented the safeguards, wording and tests.
- **Verification:** Native macOS SSD `make all`: PASS=121/WARN=0/ERROR=0 (18 models, 103 dbt tests), 15 reconciliation controls, 23 Python tests, six dashboard SQL checks. Ruff with `--no-cache` and whitespace checks passed. This slice did not rebuild Docker.

## Average resolution hours — verified slice

- **Source and eligibility:** `generate.py` supplies naive opening/resolution timestamps; silver validation excludes contradictory dates and invalid satisfaction scores. Use all accepted records with a recorded resolution, irrespective of customer attribution. Of 496 accepted tickets, 460 have a resolution and 36 do not. A recorded same-time resolution is a valid zero; a missing resolution is not zero.
- **Meaning and grain:** `config/kpis.yml` defines total completed elapsed hours divided by `resolved_ticket_count`, at opening month/category. `schema.yml` documents both fields. Later-month resolutions remain in their opening cohort and can revise its average. This is continuous elapsed time for completed cases, not business hours, backlog age or resolution-month throughput; all-unresolved groups yield null. Group means must be weighted by completed counts if subsequently aggregated.
- **Transformation and precision:** `mart_support_health.sql` now uses timestamp subtraction and elapsed seconds converted to hours. Whole-hour-boundary counting previously mismeasured fractional-hour intervals; current generated durations were all whole hours, so all 48 pre-existing count/average/satisfaction rows are unchanged after the rebuild. `resolved_ticket_count` exposes the denominator.
- **Checks:** `assert_support_resolution_reconciles.sql` reads silver directly and checks count, mean, null states and finite nonnegative values. The release control in `fieldforge/reconciliation.py` independently uses Python timedeltas, compares every group, and rejects duplicates, missing groups, incorrect counts/means and invalid null states. Eight focused Python cases execute the actual model/test SQL and detect output corruption. A half-hour resolution across month end plus an instant resolution averages 0.25 hours over two completed tickets; unresolved records are excluded. This is a purpose-built test fixture, not a claimed production row.
- **Query/display:** `dashboard/queries.py` retains opening month/category and exposes both mean and completed count. The existing support-bar tooltip shows completed tickets and the mean to two decimals with `h`; no completed duration formats as Not available. Caption explains eligibility and late updates. Browser inspection after native restart verified the caption and March 2026 billing tooltip (18 completed, 61.06 h), agreeing with direct SQL. The rebuilt Docker dashboard also passed health and scoped chart/caption rendering checks, and container SQL matched these values. This is not full dashboard acceptance.
- **Learner attribution:** Aneesh first treated the unknown duration as zero and divided by two; he then selected one completed ticket but initially described an instant resolution as excluded. After clarification he stated, “we cannot yet calculate its completed duration.” Agent calculated and queried the resulting 40-hour average for real `TKT-000459` and `TKT-000288`. Do not attribute the final arithmetic, SQL, or implementation to Aneesh.
- **Verification:** Native SSD `make all` passed PASS=123/WARN=0/ERROR=0 (18 models, 105 data tests), four gold exports, 16 release controls, 31 Python tests and six dashboard SQL checks. The rebuilt Linux/x86_64 container passed the same full gate plus Ruff, with isolated generated data and retained JSON evidence in `artifacts/docker-resolution-verification/`. The build excludes the host `.uv-python` runtime after a real container lint failure exposed it. Ruff and whitespace checks passed. Full September/account group is separately 596 hours / 11 completed = 54.181818 hours; the two-ticket exercise is not the full-month result.

## Remaining KPI coverage

| KPI family | Evidence and remaining work |
|---|---|
| Active subscribers | Month-end learner checkpoint and source comparison completed at `58d2ec7`; do not repeat the exercise. Continue any remaining edge-case/display assessment within the overall audit. |
| Logo churn | Aneesh's March Premium arithmetic is verified in the worklog. `fieldforge/cli.py` still has no independent full-series churn control. `dashboard/queries.py` retrieves churn, but `business_page` does not display it. Decide intended presentation only through a learner checkpoint. |
| Support ticket count | Verified above for accepted opening-month demand. |
| Average resolution hours | Verified above, including null/zero eligibility, elapsed precision, denominator and current tooltip. |
| Average satisfaction | Next. Mart calculates `avg_csat`; no registry entry or independent release control yet. Do not infer validity from a passing ticket-count control. |
| Revenue and attribution | Historical controls exist in `fieldforge/cli.py`; finish source-to-mart monthly/type/currency and displayed aggregation review. Whole-company cents equality alone cannot certify every currency group. |
| Order coverage, variance, accepted lines | Historical tests and controls exist; complete the requested registry-to-display checklist without altering deliberate unresolved-line governance. |

## Prioritized working findings

| Priority | Finding and evidence | Value, effort and trade-off |
|---|---|---|
| Required before portfolio completion | Remaining KPI coverage above; `docs/acceptance-criteria.md` still leaves KPI agreement and all source totals open. | Prevent unsupported trust claims. Moderate, bounded KPI-by-KPI work; retain architecture. |
| Required before portfolio completion | Concurrent native dashboard read during `make all` produced a DuckDB file-lock exception in `order_integrity_page`; reload after dbt completed recovered. | Reproducible run/refresh guidance and proportionate handling belong in the later operational slice. Small-to-moderate effort; no claim of concurrent serving during rebuild. |
| Required before portfolio completion | `docs/acceptance-criteria.md` says unticked means no current evidence, while worklog contains executed checks for several unticked criteria. | Reconcile dated acceptance evidence after KPI work. Small documentation effort; never tick boxes from existence of code alone. |
| Valuable enhancement | Source timestamps have no timezone; the ticket registry now discloses supplied-calendar semantics. `generate.py` creates naive timestamps. | A timezone contract would improve a real handover. Requires an explicit business policy; do not invent one for the synthetic prototype. |
| Optional polish | `docs/project-recap.html` contains historical 119/119 node counts. | Refresh presentation once the audit is finished. Small effort, no current correctness benefit. |
| Out of scope | Paid services, production PII, streaming and distributed production scale are excluded by `docs/product-specification.md`. | Preserve zero-cost local scope; expansion requires explicit authorization. |

## Nine-area assessment coverage

| Area | Current evidence and review limit |
|---|---|
| Data and KPI correctness | Ticket-count and resolution-time slices verified; other KPI coverage remains above. |
| Architecture and engineering | Accepted Parquet, dbt marts and direct dashboard queries are traceable in the inspected files. No evidence here justifies replacing the architecture. |
| Testing and operational resilience | New control catches group-level corruption; native and rebuilt Docker gates pass. Concurrent rebuild lock observed; recovery handling remains open. |
| Dashboard usability and decision value | Support wording now distinguishes accepted arrivals from resolutions/backlog. Broader dashboard decision-value review is pending. |
| Customer implementation narrative | `docs/customer-brief.md` and handover/worklog exist; narrative acceptance has not been re-audited in this slice. |
| Documentation and reproducibility | Updated README/continuity for this milestone; acceptance-table consistency remains open. Rebuilt Docker verification passed; no new clean-clone verification claimed. |
| Portfolio differentiation | Existing traceability and failure-detection evidence are concrete. Resume/presentation claim review remains pending; synthetic local evidence only. |
| Demo readiness | Support chart renders after pipeline completion. Full rehearsal is deferred until KPI audit completion. |
| Honest limitations and claims | Accepted-only demand, sparse groups, naive timestamps, scoped native/container verification and unverified KPI families are explicit. Public release and main actions remain unauthorized. |
