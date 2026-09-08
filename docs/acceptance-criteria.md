# Acceptance criteria and release gate

- [ ] Fresh clone completes `make setup && make all` without credentials or paid services.
- [ ] Repeated seed produces byte/logically equivalent source records and stable business keys.
- [ ] Planted-error counts match `config/planted_errors.yml`.
- [ ] Every bronze row appears exactly once in silver accepted or quarantine outputs.
- [ ] Every quarantine row includes source, rule code, reason, raw key, and run ID.
- [ ] Identity crosswalk covers every accepted source identity and records match method/confidence.
- [x] Facts have valid foreign keys and declared grain uniqueness. Evidence: dbt build 2026-09-08, PASS=118, including relationship tests from `fct_revenue` and `fct_order_item` to `dim_customer`, `dim_product`, and `dim_date`, plus grain-uniqueness tests on both facts and all four marts.
- [ ] Revenue, order, subscriber, and support totals reconcile to accepted sources.
- [ ] KPI registry, dbt mart SQL, tests, and dashboard labels agree.
- [ ] Dashboard smoke check executes every production query.
- [ ] Optional PySpark transformation matches the Pandas silver order projection.
- [ ] CI and Docker definitions exercise the supported workflow.
- [ ] Documentation includes architecture, model, discovery, handover, troubleshooting, benchmark, resume bullets, and demo path.
- [ ] `ASTRA_WORKLOG.md` contains current verification evidence and unresolved limitations.

Evidence for every criterion above is recorded with its run date in `ASTRA_WORKLOG.md`. An unticked box means no current evidence exists, not that the check is expected to fail.
