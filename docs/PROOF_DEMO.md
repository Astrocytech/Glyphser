# 5-Minute Proof Demo

Goal: show deterministic parity and reproducible divergence.

## Run

```bash
python examples/proof_demo.py
```

## Expected

- `same_seed_match` is `true`
- `different_seed_diverges` is `true`
- Evidence manifests are written under `evidence/demo/`:
  - `same_seed_run_a.{json,cbor}`
  - `same_seed_run_b.{json,cbor}`
  - `different_seed_run.{json,cbor}`
  - `summary.{json,cbor}`

## CLI quick path

```bash
glyphser run --example hello --tree
```

This verifies built-in fixture determinism and prints evidence paths + core hashes.
