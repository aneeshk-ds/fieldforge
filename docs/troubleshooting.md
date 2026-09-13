# Troubleshooting

- Setup reports that the lock is stale: run `uv lock`, review the dependency change, and commit `pyproject.toml` and `uv.lock` together. Do not bypass `uv sync --locked` in CI or Docker.

- Python rejected: use 3.11 through 3.13; make setup requests 3.13.
- dbt cannot find Parquet: run make pipeline from the repository root.
- Warehouse locked during `make all`: DuckDB permits one writer. Stop only FieldForge readers you own before a rebuild, or run the gate with isolated data and artifact roots. If a dashboard is already open, it reports that the rebuild is in progress; wait for the gate to finish and refresh. Do not restart Docker Desktop or delete data.
- Dashboard warehouse missing: run make all first.
- Reconciliation fails: inspect artifacts/reconciliation.json and compare accepted silver totals with fct_revenue; never bypass the gate.
- Spark cannot find PySpark: install the declared extra with `uv pip install --python .venv/bin/python -e '.[spark]'`; the Make target binds both Spark Python processes to this environment.
- Spark reports no Java runtime on macOS even when Homebrew Java 17 is installed: run with `JAVA_HOME=/usr/local/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home PATH=/usr/local/opt/openjdk@17/bin:$PATH make spark`.
- Docker verification requires a working Docker CLI and engine. Check `docker context show`, `docker info`, and existing workloads before changing anything; do not restart Docker Desktop or remove unrelated resources to clear a FieldForge application error.
- Clean rebuild: make clean removes only generated data and artifacts; make all recreates them.
