# Architecture

## Layered View

```text
User Code
   ↓
Glyphser Public API (`glyphser.public`)
   ↓
Runtime Core (`runtime/glyphser/api`, `runtime/glyphser/model`)
   ↓
Deterministic Execution Layer (`runtime/glyphser/model`, `runtime/glyphser/tmmu`)
   ↓
Evidence Builder (`runtime/glyphser/trace`, `runtime/glyphser/checkpoint`, `runtime/glyphser/registry`)
   ↓
Conformance Validator (`tests/`, `tooling/`, `evidence/`)
```

## Design Notes

- Public modules are intentionally thin wrappers around proven runtime components.
- Runtime components preserve deterministic behavior through canonical encoding and stable hashing.
- Evidence outputs are designed to be machine-verifiable in CI and replay flows.
