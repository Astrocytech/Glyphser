# Deterministic Benchmark Registry

Registry file:
- `artifacts/expected/benchmarks/registry.json`

Gate:

```bash
python tooling/benchmarks/benchmark_registry_gate.py
```

The gate enforces:
- latency thresholds from `evidence/benchmarks/latest.json`
- deterministic parity/divergence requirements from `evidence/benchmarks/variance_impact.json`
