# Customer discovery guide

## Before implementation

Confirm system owners, extracts, cadence, retention, timezone, currencies, refund semantics, subscriber lifecycle, customer-merge authority, PII restrictions, SLA, and KPI approvers. Request representative samples plus row counts and control totals.

## Contract workshop

For each source capture grain, primary key, change semantics, required fields, enums, timestamp timezone, late-arrival behavior, deletion signal, financial controls, and owner. Classify violations as reject, warn, or accept-with-default.

## Identity and KPI sign-off

Agree which identifiers are verified, how shared emails/phones are handled, the acceptable false-merge rate, and who resolves ambiguity. Review YAML definitions and hand-calculated examples with named Finance and Growth approvers.
