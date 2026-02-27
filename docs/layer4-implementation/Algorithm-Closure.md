# Deterministic Algorithm Closure

Status: COMPLETE

## Scope
This document records the closure of remaining algorithmic ambiguity for codegen readiness. It points to canonical definitions already present in the spec.

## Closed Areas (Canonical Sources)
- Canonical serialization rules: `docs/layer1-foundation/Canonical-CBOR-Profile.md`
- Error semantics and deterministic fields: `docs/layer1-foundation/Error-Codes.md`
- Operator registry semantics and signature digest rules: `docs/layer1-foundation/Operator-Registry-Schema.md`
- Replay determinism and E0/E1 comparisons: `docs/layer2-specs/Replay-Determinism.md`
- Trace ordering, required fields, and hash gate rules: `docs/layer2-specs/Trace-Sidecar.md`
- Checkpoint hash identities and restore invariants: `docs/layer2-specs/Checkpoint-Schema.md`
- Execution certificate required fields and hash bindings: `docs/layer2-specs/Execution-Certificate.md`
- Reference pseudocode mapping: `docs/layer4-implementation/Reference-Implementations.md`
- Determinism profile tie-breaks and numeric policy: `docs/contracts/DETERMINISM_PROFILE_v0.1.md`

## Numeric Policy (Frozen)
- Floating-point format: IEEE-754 binary64.
- NaN/Inf: invalid unless explicitly permitted by contract (see Canonical CBOR profile).
- Rounding: round-to-nearest ties-to-even for critical paths.
- Approx-equality: `EPS_EQ=1e-10`, `EPS_DENOM=1e-12` (see Reference Implementations).

## Tie-Breaks (Frozen)
- Canonical CBOR map key ordering by canonical encoded key bytes.
- Trace ordering by `(t, rank, operator_seq)`.
- Registry and catalog sorting lexicographically by UTF-8 bytes.

## Status
Algorithmic ambiguity closed for codegen purposes; remaining work is implementation and test coverage.
