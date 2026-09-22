# Repository structure

- `config/`: executable source schemas, tool evidence, KPI definitions, and planted-error governance.
- `fieldforge/`: orchestration, contracts, non-SQL transformations, independent controls, and portfolio checks.
- `dbt/`: analytics engineering project and lineage graph.
- `dashboard/`: decision interface, query registry, and read-only SQL Workbench.
- `spark/`: parity implementation for selected transformations.
- `tests/`: contract drift, behavior, reconciliation, corruption, and rendered-app assertions.
- `docs/`: implementation, operating, and portfolio package.
- `data/`: generated source/bronze/silver/quarantine/gold outputs (ignored).
- `artifacts/`: profiles, manifests, reconciliation and benchmark reports (ignored).
