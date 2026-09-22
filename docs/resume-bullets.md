# Resume-ready bullet options

- Built an end-to-end customer-data onboarding platform with Python 3.13, Pandera, PyYAML, Parquet, DuckDB, and dbt, converting 10,163 synthetic CRM, billing, commerce, and support records into 18 dimensional models with no silent row loss.
- Designed strict pre-ingestion source contracts and rule-coded quarantine controls that reconciled all 10,163 bronze rows to 10,134 accepted plus 29 rejected records while retaining provenance, raw keys, run IDs, and human-readable reasons.
- Implemented explainable identity resolution and currency-safe revenue governance across 96 month/type/currency groups, preserving unresolved valid transactions as unattributed instead of guessing customer relationships.
- Delivered a Streamlit/Plotly operations and KPI product backed by seven production SQL checks, 20 independent source-to-mart controls, four gold exports, and regression coverage for metric boundaries and rendered UI contracts.
- Reproduced the full workflow on native macOS, hosted Linux CI, and rebuilt Linux/x86_64 containers; added Java 17/PySpark parity over all 1,494 accepted order IDs, full-history Gitleaks scanning, and an executable 39-tool evidence audit.

## Claim boundary

These bullets describe the repository's implemented and verified behavior. The project uses synthetic data and does not claim public cloud deployment, production traffic, real-PII controls, high availability, or distributed Spark scale.
