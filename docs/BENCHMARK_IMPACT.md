# Benchmark Impact

This project tracks runtime overhead and determinism signal quality.

## Run benchmark suite

```bash
python tooling/benchmarks/run_benchmarks.py
python tooling/benchmarks/variance_impact.py
```

## Outputs

- `evidence/benchmarks/latest.json`: runtime latency metrics
- `evidence/benchmarks/variance_impact.json`: deterministic parity vs synthetic divergence signal behavior

## Interpretation

- Low latency overhead indicates practical CI usage.
- Same-seed digest stability validates deterministic parity checks.
- Different-seed digest divergence validates meaningful change detection.
