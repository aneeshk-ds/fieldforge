# Ten-minute demo path

1. State the customer problem and zero-cost/no-secrets constraint.
2. Show the planted-error manifest, generate sources, and inspect profiling.
3. Compare bronze, silver, and quarantine counts and rule codes.
4. Explain precision-first identity matching using the crosswalk.
5. Trace dbt lineage from staging through revenue fact to KPI marts.
6. Open the dashboard, filter Orders to `ORDER_DATES_INVALID`, and inspect `ORD-0000028`. Show the contradictory event timeline, absent dispatch field, retained source row, and source-owner evidence request.
7. Show the SQL traceability panel, then run tests and reconciliation; close with production extensions.

Reviewer commands: make setup, make all, then make dashboard.
