# Acceptance criteria and release gate

- [x] Fresh clone completes `make setup && make all` without credentials or paid services. Evidence: disposable clone `/private/tmp/fieldforge-clean-34d7478` at commit `34d7478`, 2026-09-13; 87 locked packages resolved and the complete native gate passed.
- [x] Repeated seed produces byte/logically equivalent source records and stable business keys. Evidence: the full native, rebuilt Docker, Compose, and disposable-clone runs reproduced all six handoff SHA-256 hashes on 2026-09-13.
- [x] Planted-error counts match `config/planted_errors.yml`. Evidence: `artifacts/synthetic_manifest.json`, 2026-09-13: customers 7, subscriptions 4, invoices 4, orders 6, order items 4, tickets 4.
- [x] Every bronze row appears exactly once in silver accepted or quarantine outputs. Evidence: `artifacts/validation_summary.json`, 2026-09-13: 10,163 bronze = 10,134 accepted + 29 quarantined, with every source marked reconciled.
- [x] Every quarantine row includes source, rule code, reason, raw key, and run ID. Evidence: automated validation and dashboard-quality tests passed in the 107-test full gate on 2026-09-13.
- [x] Identity crosswalk covers every accepted source identity and records match method/confidence. Evidence: crosswalk and attribution tests plus the full reconciliation gate passed on 2026-09-13; valid unresolved identities remain explicitly unattributed.
- [x] Facts have valid foreign keys and declared grain uniqueness. Evidence: the 2026-09-13 dbt build passed all 140 nodes, including fact relationships and grain tests, and the independent reconciliation passed all 20 controls.
- [x] Revenue, order, subscriber, and support totals reconcile to accepted sources. Evidence: all 20 controls in `artifacts/reconciliation.json` are true on 2026-09-13.
- [x] KPI registry, dbt mart SQL, tests, and dashboard labels agree. Evidence: `docs/kpi-audit.md` closes each KPI path; the final order audit adds direct-source dbt and Python reconstruction plus rendered-label tests.
- [x] Dashboard smoke check executes every production query. Evidence: seven of seven production queries passed natively, in the rebuilt image, through Compose, and from the disposable clone on 2026-09-13.
- [x] Optional PySpark transformation matches the Pandas silver order projection. Evidence: Java 17.0.20 / PySpark 4.0.0 checked all 1,494 accepted orders with zero missing or unexpected IDs on 2026-09-13.
- [ ] CI and Docker definitions exercise the supported workflow. Dockerfile and Compose passed full isolated `linux/amd64` gates on 2026-09-13; hosted CI for the final milestone is still pending.
- [x] Documentation includes architecture, model, discovery, handover, troubleshooting, benchmark, resume bullets, and demo path. Evidence: linked documentation and local-link checks reviewed on 2026-09-13.
- [x] `ASTRA_WORKLOG.md` contains current verification evidence and unresolved limitations. Evidence: the 2026-09-13 entry records results, scope, attribution, and deferred interview grading.

Evidence for every criterion above is recorded with its run date in `ASTRA_WORKLOG.md`. An unticked box means no current evidence exists, not that the check is expected to fail.
