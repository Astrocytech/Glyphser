# Benchmarks

Glyphser benchmarks are produced by:

```bash
python tooling/benchmarks/run_benchmarks.py
```

Latest results are written to:
- `evidence/benchmarks/latest.json`

Tracked metrics:
- Interface hash computation latency.
- Runtime API status call latency.
- Runtime API evidence call latency.

These metrics are intended for trend tracking and regression detection.
