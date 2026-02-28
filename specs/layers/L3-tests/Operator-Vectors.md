# Glyphser Operator Vector Format

Status: DRAFT

This document defines the canonical on-disk layout and minimal schema for per-operator conformance vectors.

## Storage Layout (Normative)
- Root directory: `artifacts/inputs/vectors/primitives/operators/`
- One file per operator.
- Filename rule: replace `.` with `_` in `operator_id` and append `.json`.
  - Example: `Glyphser.Data.NextBatch` -> `artifacts/inputs/vectors/primitives/operators/Glyphser_Data_NextBatch.json`

## Minimal Vector Schema (Normative)
Each file MUST be a JSON object with:
- `operator_id` (string)
- `vectors` (array)

Each vector entry MUST contain:
- `case_id` (string)
- `request` (object)
- `expected` (object)

`expected` MUST include either:
- `error` (object), or
- `response` (object)

## Determinism Rules
- Vectors are authored before implementation.
- Any change to vectors requires a deterministic re-materialization step and a rationale.
