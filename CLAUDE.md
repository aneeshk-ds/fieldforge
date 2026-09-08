# FieldForge continuation guide

This is the local continuity contract for Claude Code or any replacement development agent. Continue in this repository; do not recreate it or clone over it.

## Repository

- Local path: `/Users/aneeshkumar/Documents/ChatGPT/FieldForge`
- Private remote: `https://github.com/aneeshk-ds/fieldforge`
- Default branch: `main`
- Product: zero-cost Customer Data Onboarding Platform for fictional customer Northstar Commerce
- Cost rule: require no paid API, secret, cloud billing, proprietary warehouse, or paid dataset

Before changing anything, run:

```bash
cd "/Users/aneeshkumar/Documents/ChatGPT/FieldForge"
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
- dbt dimensions, revenue fact, KPI marts, tests, reconciliation, and evidence artifacts
- Streamlit/Plotly command center plus a guided DuckDB SQL Lab
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

## Governed decisions already made

1. Invalid records are quarantined for investigation, never silently discarded.
2. Email normalization lowercases and removes surrounding whitespace; storefront identity remains a separate field.
3. Order grain is one row per order; the storefront customer ID represents the customer across orders.
4. Supported currencies are USD, CAD, and GBP. Never sum them into one monetary total without an approved FX model.
5. Unresolved identity must not be guessed. Valid revenue remains in company totals, carries `attribution_status = 'unattributed'`, has a null customer key, and is excluded from customer-level metrics.
6. Source-event contradictions require source-owner evidence before correction.

## Next implementation sequence

1. Confirm the current branch and hosted CI are green.
2. Complete dimensional coverage and explicitly declare fact grains and key tests.
3. Isolate Python test outputs so tests never replace demo run metadata.
4. Audit and correct synthetic customer/order chronology.
5. Produce larger seeded scale profiles and reproducible benchmarks without overstating laptop results.
6. Verify Docker on a Docker-capable host and PySpark parity on a Java-capable host.
7. Lock the complete dependency environment and execute a clean-clone verification.
8. Finish customer handover, troubleshooting, portfolio story, screenshots, and demo rehearsal.
9. Request explicit user approval before changing the private repository to public.

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

> Resume FieldForge in `/Users/aneeshkumar/Documents/ChatGPT/FieldForge`. Read `CLAUDE.md`, `README.md`, and the newest entries in `ASTRA_WORKLOG.md`. Inspect Git status and recent commits, verify rather than assume the previous agent's claims, preserve existing work, and continue from the first unfinished item. Keep teaching Aneesh through the project and maintain the same bidirectional handoff before stopping.

Use this prompt when returning to Claude:

> Resume FieldForge in `/Users/aneeshkumar/Documents/ChatGPT/FieldForge`. Read `CLAUDE.md`, `README.md`, and the newest entries in `ASTRA_WORKLOG.md`. Inspect Git status and recent commits, verify rather than assume the previous agent's claims, preserve existing work, and continue from the first unfinished item. Keep teaching Aneesh through the project and maintain the same bidirectional handoff before stopping.
