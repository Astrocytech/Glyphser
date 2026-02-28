# Inputs

Deterministic input assets used by runtime validation and conformance tooling.

## Structure
- `fixtures/`: concrete reproducible fixtures.
- `vectors/`: executable vectors organized by:
  - `suites/` for scenario/suite vectors.
  - `primitives/` for canonical primitive vector sets.

## Rules
- Inputs are data-only (no importable runtime code).
- Vector manifests must reference paths under `artifacts/inputs/vectors/`.
