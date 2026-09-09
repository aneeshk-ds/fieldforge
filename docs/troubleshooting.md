# Troubleshooting

- Setup reports that the lock is stale: run `uv lock`, review the dependency change, and commit `pyproject.toml` and `uv.lock` together. Do not bypass `uv sync --locked` in CI or Docker.

- Python rejected: use 3.11 through 3.13; make setup requests 3.13.
- dbt cannot find Parquet: run make pipeline from the repository root.
- Warehouse locked: stop Streamlit or another DuckDB client and rerun.
- Dashboard warehouse missing: run make all first.
- Reconciliation fails: inspect artifacts/reconciliation.json and compare accepted silver totals with fct_revenue; never bypass the gate.
- Spark cannot find PySpark: install the declared extra with `uv pip install --python .venv/bin/python -e '.[spark]'`; the Make target binds both Spark Python processes to this environment.
- Spark reports no Java runtime on macOS even when Homebrew Java 17 is installed: run with `JAVA_HOME=/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home PATH=/usr/local/opt/openjdk@17/bin:$PATH make spark`.
- Docker verification requires a working Docker CLI and engine. This host has neither, so the image remains runtime-unverified even though its Compose dependencies are statically checked.
- Clean rebuild: make clean removes only generated data and artifacts; make all recreates them.
