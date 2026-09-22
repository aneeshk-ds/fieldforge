# Ten-minute demo path

1. **0:00–0:45 — Frame the customer problem.** Northstar Commerce has six imperfect extracts, a zero-cost/no-secrets constraint, and a requirement that invalid or unmatched data must never silently disappear.
2. **0:45–2:15 — Show quality accounting.** Open Data quality, reconcile 10,163 received rows to 10,134 accepted plus 29 quarantined, and explain why 31 rule failures can belong to 29 records.
3. **2:15–3:45 — Triage one retained exception.** Filter Orders to `ORDER_DATES_INVALID`, inspect `ORD-0000028`, and show the contradictory timeline, absent dispatch field, preserved row, and source-owner evidence request.
4. **3:45–5:30 — Show governed business health.** Explain currency-separated revenue and attribution, the month-end active-subscriber population, logo churn with its denominator, and opening-month support measures with completed/rated counts.
5. **5:30–7:00 — Show order-line integrity.** Reconcile 3,021 accepted lines: 3,013 linked to accepted headers and eight retained without one. Inspect the one known quarantine impact and keep the two unexplained gaps visibly unresolved.
6. **7:00–8:15 — Trace lineage and contracts.** Move from source contracts and KPI registry through Parquet, dbt dimensions/facts/marts, direct dashboard SQL, and retained JSON controls.
7. **8:15–9:15 — Prove delivery.** Show the latest `make verify`, rebuilt Linux/x86_64, Spark parity, portfolio receipt, and hosted CI evidence.
8. **9:15–10:00 — Close honestly.** State the local synthetic scope, naive-timestamp and no-FX boundaries, production extensions, and private-release boundary.

Reviewer commands: `make setup`, `make all`, `make portfolio-check`, then `make dashboard`. The SQL Workbench is optional for read-only operational investigation.
