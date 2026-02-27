# Operator Readiness Checklist

Each operator must satisfy this checklist before being marked "semantics complete":

1. Numeric policy documented (rounding, tolerance, NaN/Inf handling).
2. Edge cases documented with at least one vector.
3. Determinism class confirmed and tested.
4. Error codes fully covered with vectors.
5. Canonical example added under `docs/examples/operators/`.
6. Implementation matches vectors without manual intervention.
7. Algorithm-Closure consistency verified.
