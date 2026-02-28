# Operator Readiness Checklist

Each operator must satisfy this checklist before being marked "semantics complete":

1. Numeric policy documented (rounding, tolerance, NaN/Inf handling).
2. Edge cases documented with at least one vector.
3. Determinism class confirmed and tested.
4. Error codes fully covered with vectors.
5. Canonical example added under `docs/examples/operators/`.
6. Implementation matches vectors without manual intervention.
7. Algorithm-Closure consistency verified.

## Operator Status (Current)
- `Glyphser.Model.ModelIR_Executor`: numeric policy documented (binary64 reductions per spec; reference driver uses Python float); edge-case vector added (shape mismatch); determinism class validated; error codes covered by vectors; canonical example present.
- `Glyphser.Model.Forward`: numeric policy inherited from ModelIR_Executor; edge-case vector present; determinism class validated; error codes covered by vectors; canonical example present.
- `Glyphser.TMMU.PrepareMemory`: numeric policy not applicable (integer-only layout); edge-case vectors present (alignment/overflow/capacity); determinism class validated; error codes covered by vectors; canonical example present.
- `Glyphser.Backend.LoadDriver`: numeric policy not applicable; edge-case vectors present; determinism class validated; error codes covered by vectors; canonical example present.
