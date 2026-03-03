# Tutorial: Reproducible ML Pipeline Check

This walkthrough shows how to add Glyphser to a simple ML workflow.

## 1) Install

```bash
python -m pip install -e .[dev]
```

## 2) Run deterministic fixture gate

```bash
glyphser run --example hello --tree
```

Expected: `VERIFY hello-core: PASS` and stable hash outputs.

## 3) Run proof demo (parity + divergence)

```bash
python examples/proof_demo.py
```

Expected in `evidence/demo/summary.json`:
- `same_seed_match: true`
- `different_seed_diverges: true`

## 4) Add to CI

Use the template at `docs/ci/github-actions-glyphser-gate.yml` and make it a required check.

## 5) Keep release verification in your pipeline

```bash
make release-check
```
