# Contracts

Machine-readable contract artifacts for Glyphser.

## Scope
- Canonical contract payloads (`*.json`, `*.cbor`, OpenAPI).
- Registry and catalog artifacts used by gates and release tooling.

## Rules
- Contracts are normative inputs.
- Keep schema-compatible changes synchronized with `specs/schemas/` and `specs/layers/` references.
- Regenerate derived artifacts through tooling; do not hand-edit generated hashes.
