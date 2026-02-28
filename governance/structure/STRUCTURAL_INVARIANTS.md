# Structural Invariants

These invariants define non-negotiable repository structure boundaries.

## Invariants
- Machine vectors must be canonical under `artifacts/inputs/conformance/`.
- Test code must not store vector JSON files under `tests/`.
- Runtime code in `runtime/` must not import or reference `governance/`, `product/`, or `evidence/` paths.
- Legacy vector path `tests/conformance/vectors/` must not appear in active references.
- Operator conformance vectors are canonical under `artifacts/inputs/conformance/primitive_vectors/operators/`.
- Specs operator examples under `specs/examples/operators/` are illustrative-only and must not be referenced by test/tooling execution paths.
- Generated artifacts must remain partitioned under:
  - `runtime/glyphser/_generated/`
  - `artifacts/generated/stable/deploy/`
  - `artifacts/inputs/state_snapshots/`
  - `artifacts/generated/stable/metadata/`
- `artifacts/generated/tmp/` is local-only temporary output and must not be committed (except `.gitkeep`).
- Runtime generated stubs are canonical under `runtime/glyphser/_generated/`; cleanroom validation copies are transient under `artifacts/generated/tmp/codegen_staging/cleanroom_validation/`.
- Legacy generated locations are forbidden:
  - `artifacts/generated/models.py`, `operators.py`, `validators.py`, `error.py`, `bindings.py`
  - `artifacts/generated/codegen/clean_build/`
  - `artifacts/generated/codegen_manifest.json`
  - `artifacts/generated/input_hashes.json`
  - `artifacts/generated/runtime/`
  - `artifacts/generated/runtime_state/`
- Product-facing technical docs must reference canonical `specs/` and/or `specs/schemas/` sources.
- `specs/policies/` is normative for conformance; `product/handbook/policies/` is product-operational and non-normative.
- All schemas under `specs/schemas/layers/` must resolve to a mapped source document through `governance/structure/spec_schema_map.json`.
- Project inventory output is evidence and must be generated under `evidence/gates/structure/PROJECT_FILE_INVENTORY.md`.
- Runtime (`runtime/`) must not import cross-domain modules (`tooling`, `artifacts`, `evidence`, `governance`, `product`, `specs`).

## Enforcement
- Gate command: `python3 tooling/quality_gates/structural_invariants_gate.py`
- Gate command: `python3 tooling/quality_gates/domain_dependency_gate.py`
- Gate command: `python3 tooling/quality_gates/spec_schema_map_gate.py`
- Gate command: `python3 tooling/quality_gates/spec_link_gate.py`
- Evidence report: `evidence/gates/structure/structural_invariants.json`
- Evidence report: `evidence/gates/structure/domain_dependency_gate.json`
- Evidence report: `evidence/gates/structure/spec_schema_map.json`
- Evidence report: `evidence/gates/structure/spec_link_gate.json`
- Pipeline integration: `tooling/commands/push_button.py`
