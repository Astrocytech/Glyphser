# External Validation Pack

This pack helps publish one external anchor quickly.

## Option A: 90-second terminal cast

Record this exact flow:

```bash
python -m pip install glyphser
glyphser run --example hello --tree
python examples/proof_demo.py
```

Show only:
- PASS line
- hash outputs
- evidence folder tree

## Option B: short technical post outline

1. Problem: ML reproducibility claims are hard to verify.
2. Approach: deterministic execution evidence with stable hashes.
3. Demo: same seed parity + changed seed divergence.
4. CI integration: one required gate command.
5. Limits: current scope is single-host CPU-first validation.
