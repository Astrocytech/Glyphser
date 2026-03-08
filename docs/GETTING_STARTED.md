# Getting Started

This guide takes you from install to reproducibility verification in under 10 minutes.

## 1) Install

```bash
python -m pip install -e .[dev]
```

## 2) Run the built-in deterministic check

```bash
glyphser run --example hello --tree
```

Expected output includes:
- `VERIFY hello-core: PASS`
- `Trace hash`, `Certificate hash`, `Interface hash`
- paths to evidence files

## 3) Run a real parity/divergence demo

```bash
python examples/proof_demo.py
```

This demonstrates:
- Same seed => same digest
- Different seed => different digest

Artifacts are emitted under `evidence/demo/`.

## 4) Verify a custom model JSON

```bash
glyphser verify --model model.json --input input.json --format json
```

## 5) Emit a snapshot manifest

```bash
glyphser snapshot --model model.json --input input.json --out evidence/snapshot.json
```

## Typical workflow summary

1. Run model verification in CI.
2. Store snapshot + evidence as build artifacts.
3. Compare digests between runs for parity/divergence decisions.
