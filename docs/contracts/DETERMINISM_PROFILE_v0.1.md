# Determinism Profile v0.1
Status: DRAFT

## Stop-the-Line Rule
If any determinism regression is detected (hash drift, ordering variance, or non-repeatable outputs), stop feature work immediately. Add or expand conformance vectors to reproduce the issue, fix determinism, and re-run verification before resuming feature development.

This document defines the constraints required for a runtime to be considered "Deterministic" under the Glyphser specification.
See `docs/layer1-foundation/Determinism-Profiles.md` for technical details.

## Canonical Serialization Rules
- All hashed artifacts MUST use canonical CBOR as defined in `docs/layer1-foundation/Data-Representation.md`.
- The canonical CBOR encoder MUST reject non-finite floats unless explicitly allowed by the numeric policy.
- Canonical JSON is permitted only where specified (e.g., certificate materialization) and MUST use a stable key ordering and whitespace-free encoding.

## Map Key Ordering
- CBOR map keys MUST be ordered by the bytewise ordering of their canonical CBOR-encoded key bytes.
- If two keys encode to identical bytes (should be impossible for distinct keys), treat as a determinism violation and reject.

## Numeric Edge-Case Policy
- Non-finite values (NaN, +/-Infinity) are disallowed unless explicitly stated in `docs/contracts/NUMERIC_POLICY_v0.1.md`.
- Floating-point values must be encoded in the shortest canonical CBOR form that preserves their value.
- Any numeric conversion MUST be explicit in the runtime and logged as a deterministic transformation in the trace.

## Tie-Break Rules
- Any ordering that could drift MUST be fixed via explicit, deterministic tie-breaks.
- Example: when two items compare equal by primary key, apply a stable secondary key based on canonical CBOR bytes.
- If a tie-break is not defined, treat as a determinism violation and fail the run.

## Replay Token Inputs
- Replay tokens MUST be derived from a deterministic, ordered set of inputs:
  - Operator id
  - Inputs (canonical CBOR)
  - Outputs (canonical CBOR)
  - Trace event index
- The exact input set and order MUST match `docs/layer1-foundation/Determinism-Profiles.md`.

## Required Evidence
- Any ambiguity decision MUST be logged in `docs/INTERPRETATION_LOG.md`.
- Every such decision MUST have a conformance vector that reproduces the case.
