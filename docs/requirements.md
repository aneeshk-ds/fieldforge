# Requirements

## Functional

- FR-01: Generate identical source records for an identical seed.
- FR-02: Preserve raw values and add source file, row number, ingest timestamp, run ID, and checksum in bronze.
- FR-03: Reject invalid rows to a queryable quarantine dataset containing one or more explicit reasons.
- FR-04: Guarantee `bronze = accepted + quarantined` at each source grain.
- FR-05: Produce an explainable identity crosswalk without merging contradictory high-confidence identifiers.
- FR-06: Build conformed dimensions and transaction/periodic facts using dbt.
- FR-07: Define each published KPI in a governed YAML registry with grain, owner, SQL source, and caveats.
- FR-08: Reconcile model totals to accepted source data within documented tolerances.
- FR-09: Dashboard queries only tested gold relations.
- FR-10: Emit profiling, run summary, reconciliation, and benchmark artifacts.

## Non-functional

- NFR-01: ₹0 incremental cost and no secrets.
- NFR-02: Linux/macOS local execution and container execution.
- NFR-03: Python 3.11–3.13 support; deterministic runs.
- NFR-04: Clear failure messages and idempotent rebuilds.
- NFR-05: CI validates formatting, tests, pipeline, dbt, and documentation references.
- NFR-06: Synthetic-only data and explicit PII handling guidance.
