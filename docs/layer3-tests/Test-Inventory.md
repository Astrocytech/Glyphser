# Glyphser Test Inventory

Status: ACTIVE

## Unit Vectors
- Canonical CBOR: `conformance/vectors/canonical_cbor/vectors.json`
- Struct validation: `conformance/vectors/struct_validation/vectors.json`
- Interface hash: `conformance/vectors/interface_hash/vectors.json`

## Integration Vectors
- Hello-core: `vectors/hello-core/vectors.json`
- Checkpoint/restore: `vectors/checkpoint-restore/vectors.json`
- Replay determinism: `vectors/replay-determinism/vectors.json`
- Registry lifecycle: `vectors/registry-lifecycle/vectors.json`
- Tracking/monitoring: `vectors/tracking-monitoring/vectors.json`
- Failure injection: `vectors/failure-injection/vectors.json`
- Perf/scale: `vectors/perf-scale/vectors.json`
- Failure injection: `vectors/failure-injection/vectors.json`
- Perf/scale: `vectors/perf-scale/vectors.json`
- Checkpoint/restore: `vectors/checkpoint-restore/vectors.json`
- Replay determinism: `vectors/replay-determinism/vectors.json`
- Registry lifecycle: `vectors/registry-lifecycle/vectors.json`
- Tracking/monitoring: `vectors/tracking-monitoring/vectors.json`

## Replay / Checkpoint
- Trace hash-chain: `tests/trace/test_compute_trace_hash.py`
- Checkpoint/certificate hashes: `scripts/run_hello_core.py` (golden verification)

## Evidence / Hash Link
- `docs/examples/hello-core/hello-core-golden.json`
- `goldens/hello-core/golden-identities.json`

## CI Gates
- Conformance: `tools/conformance/cli.py`
- Schema gate: `tools/schema_gate.py`
- Registry gate: `tools/registry_gate.py`
