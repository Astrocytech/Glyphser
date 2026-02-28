# Structural Invariants

These invariants define non-negotiable repository structure boundaries.

## Invariants
- Machine vectors must be canonical under `artifacts/inputs/vectors/`.
- Test code must not store vector JSON files under `tests/`.
- Runtime code in `src/` must not import or reference `governance/`, `product/`, or `evidence/` paths.
- Legacy vector path `tests/conformance/vectors/` must not appear in active references.
- Generated artifacts must remain partitioned under:
  - `artifacts/generated/codegen/`
  - `artifacts/generated/deploy/`
  - `artifacts/generated/runtime_state/`
  - `artifacts/generated/build_metadata/`
- Legacy generated locations are forbidden:
  - `artifacts/generated/models.py`, `operators.py`, `validators.py`, `error.py`, `bindings.py`
  - `artifacts/generated/codegen/clean_build/`
  - `artifacts/generated/codegen_manifest.json`
  - `artifacts/generated/input_hashes.json`
  - `artifacts/generated/runtime/`

## Enforcement
- Gate command: `python3 tooling/gates/structural_invariants_gate.py`
- Evidence report: `evidence/structure/structural_invariants.json`
- Pipeline integration: `tooling/push_button.py`
