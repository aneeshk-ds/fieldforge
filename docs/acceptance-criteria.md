# Acceptance criteria and release gate

- [ ] Fresh clone completes `make setup && make all` without credentials or paid services.
- [ ] Repeated seed produces byte/logically equivalent source records and stable business keys.
- [ ] Planted-error counts match `config/planted_errors.yml`.
- [ ] Every bronze row appears exactly once in silver accepted or quarantine outputs.
- [ ] Every quarantine row includes source, rule code, reason, raw key, and run ID.
- [ ] Identity crosswalk covers every accepted source identity and records match method/confidence.
- [ ] Facts have valid foreign keys and declared grain uniqueness.
- [ ] Revenue, order, subscriber, and support totals reconcile to accepted sources.
- [ ] KPI registry, dbt mart SQL, tests, and dashboard labels agree.
- [ ] Dashboard smoke check executes every production query.
- [ ] Optional PySpark transformation matches the Pandas silver order projection.
- [ ] CI and Docker definitions exercise the supported workflow.
- [ ] Documentation includes architecture, model, discovery, handover, troubleshooting, benchmark, resume bullets, and demo path.
- [ ] `ASTRA_WORKLOG.md` contains current verification evidence and unresolved limitations.
