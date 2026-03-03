# Evidence Formats

## Core hello-core files

- `artifacts/inputs/fixtures/hello-core/trace.json`
  - Ordered execution records.
  - Verifiable with `compute_trace_hash`.

- `artifacts/inputs/fixtures/hello-core/checkpoint.json`
  - Deterministic checkpoint header with manifest and registry hashes.

- `artifacts/inputs/fixtures/hello-core/execution_certificate.json`
  - Cross-links `trace_final_hash`, `checkpoint_hash`, and contract root hash.

## Security release files

- `evidence/security/sbom.json`
  - Package inventory + source commit + lock/pyproject hashes.

- `evidence/security/build_provenance.json`
  - Build context summary linking to SBOM digest.

## Benchmark files

- `evidence/benchmarks/latest.json`
  - Runtime overhead and hashing timing metrics.
