# Artifacts

Deterministic inputs, expected outputs, generated material, and release bundles.

## Contents
- `artifacts/inputs/`: fixtures and vectors used by tests and conformance.
- `artifacts/expected/`: goldens and expected result references.
- `artifacts/generated/`: generated code/build/deploy/runtime-state outputs.
- `artifacts/bundles/`: release bundle outputs and checksum manifests.

## Rule
Treat artifacts as reproducible data boundaries; avoid hand-editing generated files.
