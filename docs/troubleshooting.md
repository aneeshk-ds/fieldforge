# Troubleshooting

- Python rejected: use 3.11 through 3.13; make setup requests 3.13.
- dbt cannot find Parquet: run make pipeline from the repository root.
- Warehouse locked: stop Streamlit or another DuckDB client and rerun.
- Dashboard warehouse missing: run make all first.
- Reconciliation fails: inspect artifacts/reconciliation.json and compare accepted silver totals with fct_revenue; never bypass the gate.
- Spark fails: install the spark extra and a compatible Java runtime. Spark is optional.
- Clean rebuild: make clean removes only generated data and artifacts; make all recreates them.
