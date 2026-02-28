# Structural Invariants

These invariants define non-negotiable repository structure boundaries.

## Invariants
- Machine vectors must be canonical under `artifacts/inputs/vectors/`.
- Test code must not store vector JSON files under `tests/`.
- Runtime code in `src/` must not import or reference `governance/`, `product/`, or `evidence/` paths.
- Legacy vector path `tests/conformance/vectors/` must not appear in active references.
- Operator conformance vectors are canonical under `artifacts/inputs/vectors/conformance/operators/`.
- Specs operator examples under `specs/examples/operators/` are illustrative-only and must not be referenced by test/tooling execution paths.
- Generated artifacts must remain partitioned under:
  - `artifacts/generated/codegen/`
  - `artifacts/generated/deploy/`
  - `evidence/runtime_state/`
  - `artifacts/generated/build_metadata/`
- Legacy generated locations are forbidden:
  - `artifacts/generated/models.py`, `operators.py`, `validators.py`, `error.py`, `bindings.py`
  - `artifacts/generated/codegen/clean_build/`
  - `artifacts/generated/codegen_manifest.json`
  - `artifacts/generated/input_hashes.json`
  - `artifacts/generated/runtime/`
  - `artifacts/generated/runtime_state/`
- Product-facing technical docs must reference canonical `specs/` and/or `specs/schemas/` sources.
- All schemas under `specs/schemas/layers/` must resolve to a mapped source document through `governance/structure/spec_schema_map.json`.
- Project inventory output is evidence and must be generated under `evidence/structure/PROJECT_FILE_INVENTORY.md`.
- Runtime (`src/`) must not import cross-domain modules (`tooling`, `artifacts`, `evidence`, `governance`, `product`, `specs`).

## Enforcement
- Gate command: `python3 tooling/gates/structural_invariants_gate.py`
- Gate command: `python3 tooling/gates/domain_dependency_gate.py`
- Gate command: `python3 tooling/gates/spec_schema_map_gate.py`
- Gate command: `python3 tooling/gates/spec_link_gate.py`
- Evidence report: `evidence/structure/structural_invariants.json`
- Evidence report: `evidence/structure/domain_dependency_gate.json`
- Evidence report: `evidence/structure/spec_schema_map.json`
- Evidence report: `evidence/structure/spec_link_gate.json`
- Pipeline integration: `tooling/push_button.py`
