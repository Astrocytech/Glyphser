# Glyphser Test Coverage Gaps

Status: Updated

This document enumerates current coverage gaps between the operator registry and the test suite.

## Summary
- Total operators in registry: 27
- Operators referenced in tests: 27
- Operators missing direct test references: 0

## Missing Operators (No Direct Test References)
- None

## Immediate Actions
- Expand beyond per-operator vectors with property/fuzz tests for IR validation, schema parsing, checkpoint decode, and TMMU planner invariants.
- Add distributed chaos tests (rank loss, network partition, delayed collective).
- Add replay divergence minimization tests at scale (multi-rank long-horizon).
- Extend hello-core or create a second fixture set to exercise at least one operator from each major domain.
