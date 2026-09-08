# Implementation handover

## Delivered

Local medallion pipeline, profiling, validation and quarantine, deterministic identity crosswalk, dbt dimensions/facts/marts, KPI registry, dashboard, tests, CI, optional Spark parity, and operating documentation.

## Customer-owned configuration

Replace synthetic mappings, contract rules, enumerations, identity authority, currency policy, and KPI approvers. Do not remove validations simply to make a new extract pass.

## Operating cadence

Run make all, retain the validation and reconciliation JSON artifacts, review new rule codes, then release the dashboard. A failed reconciliation blocks release.

## Exception triage

1. Filter the exception workbench to the affected source and rule.
2. Select one record and compare its preserved values and event timeline.
3. Treat **Not supplied** as a source-contract gap and **Missing** as a supplied-but-empty value; do not silently treat them as equivalent.
4. Send the generated evidence request to the source owner and retain the original record in quarantine.
5. Correct or replay a record only after authoritative source evidence identifies the faulty value. Re-run the pipeline and confirm source-level reconciliation before release.

## Production extensions

Add incremental manifests, object storage, orchestration, catalog/observability, PII tokenization, access control, SCD2 customer history, FX policy, and a human identity-review queue as needed.
