# Use Cases

## 1) CI determinism gate

Run `glyphser run --example hello` on every PR to detect baseline determinism regressions.

## 2) Reproducibility checks in ML experimentation

Use `python examples/proof_demo.py` to validate same-seed parity and changed-seed divergence.

## 3) Audit-ready evidence bundles

Use `glyphser snapshot` to persist run outputs and digests as machine-checkable manifests.
