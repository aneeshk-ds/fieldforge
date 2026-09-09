# FieldForge continuation guide

This is the local continuity contract for Claude Code or any replacement development agent. Continue in this repository; do not recreate it or clone over it.

## Repository

- Local path: `/Volumes/AK-SSD-MAC/Codex Work/FieldForge`
- Private remote: `https://github.com/aneeshk-ds/fieldforge`
- Default branch: `main`
- Product: zero-cost Customer Data Onboarding Platform for fictional customer Northstar Commerce
- Cost rule: require no paid API, secret, cloud billing, proprietary warehouse, or paid dataset

Before changing anything, run:

```bash
cd "/Volumes/AK-SSD-MAC/Codex Work/FieldForge"
git status --short
git log -5 --oneline
sed -n '1,180p' README.md
sed -n '1,220p' ASTRA_WORKLOG.md
```

Preserve unrelated user changes. Use the existing environment when present; otherwise run `make setup`. Generated data, `.venv`, DuckDB files, and artifacts are intentionally ignored by Git.

## Current product state

- Deterministic synthetic CRM, subscription, invoice, order, order-item, and support extracts
- Bronze/silver/gold local lakehouse on Parquet and DuckDB
- Explicit rule-coded quarantine with no silent record loss
- Deterministic exact-email identity crosswalk with unmatched identities retained
- dbt sources, dimensions, revenue and order-line facts, KPI marts, tests, reconciliation, and evidence artifacts
- 18 dbt models with grain declared on every model, 101 dbt tests, and 13 reconciliation controls
- Order lines whose parent order was quarantined are retained with `order_link_status = 'order_not_accepted'`
- `mart_order_line_integrity` publishes orders whose accepted lines no longer reconcile to the header amount
- Paths resolve at call time from `FIELDFORGE_DATA_ROOT` and `FIELDFORGE_ARTIFACTS_ROOT`, so a run can be relocated
- Tests run against a temporary root and never touch the demo run; a failing run retains evidence in `artifacts/test-runs/<run-id>/`
- Streamlit/Plotly command center with a dedicated order-integrity view plus a guided DuckDB SQL Lab
- Source-aware exception workbench with raw evidence, event timeline, and source-owner request
- Company revenue includes valid unattributed transactions; customer metrics use attributed revenue only
- USD, CAD, and GBP remain separate because no FX policy has been approved
- Docker, GitHub Actions, optional PySpark slice, architecture, discovery, handover, troubleshooting, demo, and resume documents exist

The repository is a strong verified prototype, not a finished public release. Never claim the definition of done until every open item in `README.md`, `docs/acceptance-criteria.md`, and `ASTRA_WORKLOG.md` has current evidence.

## Commands

```bash
make setup       # local Python environment and dependencies
make pipeline    # source generation through gold models and reconciliation
make test        # Python tests and dashboard SQL smoke checks
make all         # one-command pipeline plus tests
make dashboard   # Streamlit command center on port 8501
```

SQL Lab:

```bash
.venv/bin/streamlit run dashboard/sql_lab.py --server.port 8502
```

Relocated run, for a benchmark or experiment that must not disturb the demo data:

```bash
FIELDFORGE_DATA_ROOT=/tmp/ff/data FIELDFORGE_ARTIFACTS_ROOT=/tmp/ff/artifacts make all
```

After tests that regenerate source files, run `make pipeline` again before demonstrating the dashboard so normal run metadata is restored. The dashboard fingerprints Parquet outputs and refreshes its cache when they change.

## Working agreement with Aneesh

- Teach through the project, not through long disconnected lectures.
- Explain the business concept, show how companies operate it, give one manageable hands-on decision or query, then turn the result into tested project work.
- Aneesh understands source grain, IDs, normalization, quarantine, reconciliation, basic SQL filtering/aggregation, and evidence-first source-owner investigation.
- SQL grouping grain, aliases, and scalar subqueries still need reinforcement, but SQL practice must support delivery rather than replace the project.
- Keep progress updates concise and maintain `ASTRA_WORKLOG.md` with decisions, errors, verification, and outcomes.
- Update the README milestone table in the same commit as completed work.
- Maintain the ambitious visual standard while keeping every displayed number traceable to models and SQL.
- Ask only when a choice materially changes business semantics, access, cost, or release scope.

## Non-negotiable learner-in-the-loop mode

The project must progress through the same short, interactive rhythm Aneesh established with Codex. Technical autonomy does not authorize skipping the learning experience or changing the agreed roadmap.

For every new concept or vertical slice:

1. In no more than five short sentences, explain what the component is, why Northstar Commerce needs it, and how a company uses it day to day.
2. Show the actual relevant table, a small readable preview, its grain, and only the columns needed for the next decision. Use the existing Streamlit dashboard or SQL Lab whenever possible; do not substitute a detached HTML preview unless Aneesh explicitly requests an export.
3. Ask exactly one manageable question. It may be one business decision or one small SQL step, never both and never a multi-part assessment.
4. Stop and wait for Aneesh's answer before advancing that teaching checkpoint. Do not answer the exercise on his behalf unless he asks.
5. If Aneesh says he does not know, is overwhelmed, or cannot do it, reduce the task immediately: explain one idea in plain language, provide a partially completed query or two-choice decision, and ask for only the missing piece.
6. After his answer, explain the result briefly, connect it to company practice, implement the agreed behavior, verify it, and show the visible outcome in the same live app.
7. Return to product delivery after the checkpoint. SQL is a supporting skill inside FieldForge, not a separate course and not the majority of a session.

Interaction constraints:

- Keep learner-facing messages concise and conversational. Do not deliver essays, manifestos, interview lectures, or a wall of schema names.
- Never ask Aneesh to query a table he cannot already see. Preview it in the SQL Lab first and list only the necessary columns.
- Never assign a query with several new SQL techniques at once. Teach one of `WHERE`, `GROUP BY`, conditional aggregation, `HAVING`, joins, or subqueries at a time.
- When a query is wrong, run it as written when safe, show what it returned, identify one issue, and let Aneesh make the next correction.
- Do not independently reprioritize the roadmap, argue for premature publication, or dismiss agreed quality gates. Suggestions may be offered briefly, but the documented sequence remains authoritative until Aneesh changes it.
- Do not make the repository public, merge branches, discard work, or broaden product scope without explicit authorization.
- Safe implementation may continue autonomously only after the current learner/business checkpoint is resolved. Preview the next milestone before beginning another large slice.
- A message such as `got it`, `yes`, or a short query answer means continue one step—not permission to skip the rest of the teaching loop or finish several milestones silently.

The target cadence is: **explain one concept → show real data → ask one small question → wait → implement → verify visually → continue**.

## Governed decisions already made

1. Invalid records are quarantined for investigation, never silently discarded.
2. Email normalization lowercases and removes surrounding whitespace; storefront identity remains a separate field.
3. Order grain is one row per order; the storefront customer ID represents the customer across orders.
4. Supported currencies are USD, CAD, and GBP. Never sum them into one monetary total without an approved FX model.
5. Unresolved identity must not be guessed. Valid revenue remains in company totals, carries `attribution_status = 'unattributed'`, has a null customer key, and is excluded from customer-level metrics.
6. Source-event contradictions require source-owner evidence before correction.
7. `created_at` is the customer's canonical first-seen date and must fall on or before that customer's earliest subscription, order, or support event. Where the two disagree, `created_at` is wrong, not the event date.

## Next implementation sequence

Branch and CI confirmation, dimensional coverage, test-output isolation, and reproducible 1×/10× local benchmarks are complete, all on branch `claudework`. See the newest `ASTRA_WORKLOG.md` entries for evidence.

1. Execute Docker on a Docker-capable host; static inspection already corrected the missing `make` dependency, but this Mac has no Docker runtime.
2. Finish customer handover, troubleshooting, portfolio story, screenshots, and demo rehearsal.
3. Request explicit user approval before changing the private repository to public.

## Branch convention

Work delivered by Claude lands on a `claudework` branch so Codex can identify it, review it, and merge or continue from it. `main` is only advanced by Aneesh or by an agent he has explicitly asked to commit there.

## Environment note

The `.venv` in this repository is macOS-only. An agent running in a Linux sandbox cannot use it and must install a separate environment outside the repository rather than replacing `.venv`. Verification produced on Linux is real but is not proof of macOS parity; say which platform produced any evidence recorded.

## Review notes for the next agent

Verify these rather than trusting the summary above.

1. **Branch state.** `claudework` carries all Claude work and has never been pushed; no GitHub credential is available in the Cowork session shell. `main` is untouched at `6ba3c96`. Run `git log --oneline main..claudework` before assuming what is in each.
2. **Platform of the evidence.** Every verification claim in the two newest worklog entries was produced on Linux in a session sandbox, not with the macOS `.venv`. Re-run `make all` on macOS before treating any of it as release evidence.
3. **The path refactor is the highest-risk change.** `fieldforge/settings.py` no longer exports `DATA`, `SOURCE`, `BRONZE`, `SILVER`, `QUARANTINE`, `GOLD`, `WAREHOUSE` or `ARTIFACTS` as constants; they are functions now. Anything written against the old names fails on import. `spark/standardize_orders.py` still builds its own paths and was not migrated.
4. **dbt now depends on an environment variable.** `profiles.yml` and `sources.yml` use `env_var('FIELDFORGE_DATA_ROOT', 'data')`. Setting it for Python but not for dbt, or the reverse, splits the two halves of a run apart.
5. **`dashboard/data_quality.py` changed signature.** `load_quality_snapshot` and `load_quarantined_record` take the data directory now, not the repository root.
6. **Order-line governance is deliberate, not a defect.** 8 accepted lines carry `order_link_status = 'order_not_accepted'` and 3 accepted orders do not reconcile to their line totals. Both are published on purpose. Do not resolve them by dropping rows or inferring a parent order.
7. **Test isolation has a boundary.** Only modules requesting the `isolated_data_root` fixture are isolated. A new mutating test that forgets it will write to the demo run again.
8. **Failed-run evidence accumulates.** `artifacts/test-runs/<run-id>/` is Git-ignored and never cleaned automatically.
9. **Streamlit width migration.** Repository-owned dashboard and SQL Lab calls now use `width="stretch"`; historical worklog text still mentions the former deprecation as past context.
10. **CI lint scope.** GitHub Actions lints only `fieldforge dashboard tests`, so `spark/` is uncovered. `ruff check .` is currently clean; keep checking the whole tree.
11. **Teaching contract.** The learner-in-the-loop section above is binding. It was violated earlier in this session and Aneesh stopped the work. One concept, real data in the live app, one question, then wait.
12. **Chronology fix changes generated data.** Regenerating with corrected `created_at` changes every source CSV checksum. Quarantine counts, revenue totals and order-line integrity figures should not move, because no validation rule or monetary model reads `created_at`. If any of them do move, stop and investigate rather than updating the documented figures.
13. **SQL Lab coverage.** The lab exposes `quarantined_orders`, `incoming_orders`, and the one-row-per-accepted-customer `customer_chronology` table. Keep future teaching tables equally small and traceable.

## Handoff discipline

Start from the first unfinished item supported by evidence, not from a claim in conversation. Inspect the current diff and generated artifacts, run the smallest relevant checks, then run `make all` and hosted CI before marking a milestone verified. Keep this file current whenever the resume procedure or major remaining-work list changes.

## Bidirectional agent-switch protocol

This file is shared continuity state, not a one-time handoff to Claude. Before Claude hands the project back to Codex—or before any development agent stops because of usage limits—it must:

1. Update `README.md` with the current milestone, honest completion status, and next action.
2. Add a dated entry to `ASTRA_WORKLOG.md` covering work performed, decisions, errors, verification evidence, and unresolved blockers.
3. Update this file if architecture, commands, governed decisions, learning state, or the next implementation sequence changed.
4. Run the strongest safe local verification available and record the exact result. Never describe an unexecuted check as passing.
5. Commit and push the checkpoint to the private `main` branch when credentials and repository state allow it. If not, leave the working tree intact and document every uncommitted file and why it was not pushed.
6. Report the final commit SHA, branch, synchronization state, tests executed, failures, open processes, and the first unfinished task.

Use this prompt when returning to Codex:

> Resume FieldForge in `/Volumes/AK-SSD-MAC/Codex Work/FieldForge`. Read `CLAUDE.md`, `README.md`, and the newest entries in `ASTRA_WORKLOG.md`. Inspect Git status and recent commits, verify rather than assume the previous agent's claims, preserve existing work, and continue from the first unfinished item. Keep teaching Aneesh through the project and maintain the same bidirectional handoff before stopping.

Use this prompt when returning to Claude:

> Resume FieldForge in `/Volumes/AK-SSD-MAC/Codex Work/FieldForge`. Read `CLAUDE.md`, `README.md`, and the newest entries in `ASTRA_WORKLOG.md`. Inspect Git status and recent commits, verify rather than assume the previous agent's claims, preserve existing work, and continue from the first unfinished item. Keep teaching Aneesh through the project and maintain the same bidirectional handoff before stopping.
