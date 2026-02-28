# Glyphser Test Inventory

Status: ACTIVE

## Unit Vectors
- Canonical CBOR: `conformance/artifacts/inputs/conformance/canonical_cbor/vectors.json`
- Struct validation: `artifacts/inputs/conformance/primitives/data_structures/vectors.json`
- Interface hash: `conformance/artifacts/inputs/conformance/interface_hash/vectors.json`

## Integration Vectors
- Hello-core: `artifacts/inputs/conformance/suites/hello-core/vectors.json`
- Checkpoint/restore: `artifacts/inputs/conformance/suites/checkpoint-restore/vectors.json`
- Replay determinism: `artifacts/inputs/conformance/suites/replay-determinism/vectors.json`
- Registry lifecycle: `artifacts/inputs/conformance/suites/registry-lifecycle/vectors.json`
- Tracking/monitoring: `artifacts/inputs/conformance/suites/tracking-monitoring/vectors.json`
- Failure injection: `artifacts/inputs/conformance/suites/failure-injection/vectors.json`
- Perf/scale: `artifacts/inputs/conformance/suites/perf-scale/vectors.json`
- Failure injection: `artifacts/inputs/conformance/suites/failure-injection/vectors.json`
- Perf/scale: `artifacts/inputs/conformance/suites/perf-scale/vectors.json`
- Checkpoint/restore: `artifacts/inputs/conformance/suites/checkpoint-restore/vectors.json`
- Replay determinism: `artifacts/inputs/conformance/suites/replay-determinism/vectors.json`
- Registry lifecycle: `artifacts/inputs/conformance/suites/registry-lifecycle/vectors.json`
- Tracking/monitoring: `artifacts/inputs/conformance/suites/tracking-monitoring/vectors.json`

## Replay / Checkpoint
- Trace hash-chain: `tests/trace/test_compute_trace_hash.py`
- Checkpoint/certificate hashes: `tooling/scripts/run_hello_core.py` (golden verification)
- Mini tracking fixture: `tests/artifacts/inputs/fixtures/test_mini_tracking_fixture.py`

## Fuzz / Property
- IR validation fuzz: `tests/fuzz/test_ir_validation_fuzz.py`
- Schema parsing fuzz: `tests/fuzz/test_schema_parsing_fuzz.py`
- Checkpoint decode fuzz: `tests/fuzz/test_checkpoint_decode_fuzz.py`
- TMMU planner invariants: `tests/fuzz/test_tmmu_planner_invariants.py`

## Chaos / Replay Scale
- Distributed chaos suite: `tests/chaos/test_distributed_chaos.py` (toggle with `GLYPHSER_ENABLE_CHAOS=1`)
- Replay divergence suite: `tests/replay/test_replay_divergence.py` (toggle with `GLYPHSER_ENABLE_REPLAY_SCALE=1`)

## Evidence / Hash Link
- `docs/examples/hello-core/hello-core-golden.json`
- `artifacts/expected/goldens/hello-core/golden-identities.json`

## CI Gates
- Conformance: `tooling/conformance/cli.py`
- Schema gate: `tooling/quality_gates/schema_gate.py`
- Registry gate: `tooling/quality_gates/registry_gate.py`
- Spec lint: `tooling/quality_gates/spec_lint.py`

## Golden Inventory
- Golden inventory: `artifacts/expected/goldens/golden_inventory.json`
- Golden inventory test: `tests/artifacts/expected/goldens/test_golden_inventory.py`

## Determinism Regression Matrix
- Matrix scaffolds: `tests/replay/test_determinism_regression_matrix.py` (toggle with `GLYPHSER_ENABLE_REGRESSION_MATRIX=1`)

## Manifest / Trace Fuzz
- Manifest parser fuzz: `tests/fuzz/test_manifest_parser_fuzz.py` (toggle with `GLYPHSER_ENABLE_FUZZ_HARNESS=1`)
- Trace parser fuzz: `tests/fuzz/test_trace_parser_fuzz.py` (toggle with `GLYPHSER_ENABLE_FUZZ_HARNESS=1`)
