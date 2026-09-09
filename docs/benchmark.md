# Benchmark protocol

Run `make benchmark` on an idle machine. The command refuses to use the demo roots, generates a deterministic workload under `data/benchmarks/<profile>/`, and writes evidence under `artifacts/benchmarks/<profile>/`. A repeat archives the previous `benchmark.json` before writing the latest result.

Override `BENCHMARK_PROFILE` and `BENCHMARK_CUSTOMERS` together to define a scale profile. The default is the learner-approved 10× profile:

```bash
make benchmark BENCHMARK_PROFILE=1x BENCHMARK_CUSTOMERS=500
make benchmark BENCHMARK_PROFILE=10x BENCHMARK_CUSTOMERS=5000
```

## Measured SSD workspace results — 9 September 2026

Hardware/software: macOS 14.8.9, x86_64, 4 logical CPUs, Python 3.13.14, DuckDB/dbt with four dbt threads. Both profiles used seed `20260907`; every run passed 18 dbt models, 101 dbt tests, 13 reconciliation controls, and six dashboard query checks.

| Profile | Cache | Customers | Source rows | Source → silver | dbt build | Total | Python peak RSS | Child peak RSS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1× | Cold | 500 | 10,163 | 8.898 s | 29.402 s | 39.137 s | Not scoped | Not scoped |
| 10× | Cold | 5,000 | 102,479 | 105.822 s | 24.685 s | 130.938 s | Not scoped | Not scoped |
| 1× | Warm | 500 | 10,163 | 14.764 s | 36.642 s | 51.861 s | 126.41 MiB | 165.04 MiB |
| 10× | Warm | 5,000 | 102,479 | 130.088 s | 24.515 s | 155.108 s | 265.81 MiB | 192.14 MiB |

The 10× profile contains 10.08× the source rows and took 3.35× the cold elapsed time or 2.99× the warm elapsed time. The repeat being slower than the first observation shows why cache labels are evidence, not a promise of speed. Peak memory values are separate per-process maxima for the Python orchestrator and completed children; they are not concurrent or system-wide peaks and must not be summed.

These are two observations on one laptop, not a production throughput, concurrency, or capacity claim. Preserve the JSON evidence and rerun on the intended deployment hardware before using the results for sizing.

## Baseline result — 2026-09-07

On the local macOS Codex sandbox with Python 3.13.14, a warm-cache default make pipeline run processed 10,163 synthetic source rows, built 11 dbt models, executed 14 dbt data tests, exported three gold marts, and reconciled financial/FK controls in 42.84 seconds wall time (21.40 seconds user CPU, 13.72 seconds system CPU). PyArrow CPU-feature probes were sandbox-restricted; this did not affect correctness. Treat this as a reproducibility baseline, not a throughput guarantee.
