# Spec-Implementation Matrix

This matrix defines required linkage between normative specs, implementation modules, and tests.

| Spec Source | Runtime/Tooling Module(s) | Required Test/Gate |
|---|---|---|
| `specs/contracts/openapi_public_api_v1.yaml` | `runtime/glyphser/api/runtime_api.py`, `glyphser/public/runtime.py` | `tooling/quality_gates/spec_impl_congruence_gate.py`, `tests/gates/test_spec_impl_congruence_gate.py` |
| `specs/contracts/interface_hash.json` | `runtime/glyphser/registry/interface_hash.py` | `tests/interface_hash/test_vectors.py`, `tooling/quality_gates/spec_impl_congruence_gate.py` |
| `specs/examples/hello-core/hello-core-golden.json` | `tooling/scripts/run_hello_core.py`, `glyphser/cli.py` | `tests/public/test_public_cli.py`, `tests/test_determinism_repeat.py` |
| `specs/schemas/evidence_metadata.schema.json` | `tooling/release/generate_evidence_metadata.py` | `tooling/quality_gates/evidence_metadata_gate.py`, `tests/release/test_evidence_metadata.py` |
| `specs/schemas/contract_schema_meta.json` + `specs/schemas/**/*.schema.json` | schema validation tooling | `tooling/quality_gates/schema_gate.py`, `tests/gates/test_spec_schema_map_gate.py` |

## Policy

- Any PR that changes a spec source in this table must update linked implementation and required tests.
- CI must fail when required tests/gates for affected rows fail.
