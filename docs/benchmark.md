# Benchmark protocol

Run make benchmark on an idle machine. It records scale and elapsed seconds in artifacts/benchmark.json. Record hardware, OS, Python version, cold/warm cache, row counts, model count, and peak memory before publishing. A single laptop timing is not a scalability claim.

## Baseline result — 2026-09-07

On the local macOS Codex sandbox with Python 3.13.14, a warm-cache default make pipeline run processed 10,163 synthetic source rows, built 11 dbt models, executed 14 dbt data tests, exported three gold marts, and reconciled financial/FK controls in 42.84 seconds wall time (21.40 seconds user CPU, 13.72 seconds system CPU). PyArrow CPU-feature probes were sandbox-restricted; this did not affect correctness. Treat this as a reproducibility baseline, not a throughput guarantee.
