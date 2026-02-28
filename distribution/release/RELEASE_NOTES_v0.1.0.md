# Release Notes v0.1.0

Status: PUBLIC-READY

## Highlights
- Deterministic hello-core reference run with reproducible identities.
- Conformance CLI for run/verify/report.
- Operator registry + interface hash generation.

## Verification
- Reproducibility guide: `docs/VERIFY.md`
- Single command: `python tooling/verify_release.py`

## Quick Verify (External, <=5 steps)
1. Clone repository and checkout the release commit/tag.
2. Create and activate a virtual environment.
3. Install runtime dependencies: `python -m pip install -e .`
4. Run `python tooling/verify_release.py`.
5. Confirm `VERIFY_RELEASE: PASS`.

## Known-Good Hash Table

| Artifact | SHA-256 |
| --- | --- |
| `evidence/conformance/reports/latest.json` | `86de4a5d30cab3a12ead92ae207bcb17fd09f7c8b498419728f7041f14e56ffe` |
| `artifacts/bundles/hello-core-bundle.tar.gz` | `a612ab112515b189f7647153bf5a92c6b1c76a35703ae74f8a67f0c0c708922c` |
| `artifacts/bundles/hello-core-bundle.sha256` | `1a992ebd1018a8b6a8c2185a19f88e345a458f4b587283b0da48fcb401df3008` |
| `evidence/repro/hashes.txt` | `1a992ebd1018a8b6a8c2185a19f88e345a458f4b587283b0da48fcb401df3008` |

Checksum source file: `docs/release/CHECKSUMS_v0.1.0.sha256`  
Signed checksum (to publish): `docs/release/CHECKSUMS_v0.1.0.sha256.asc`

## Known Limitations
- Operator registry builder uses default placeholder metadata for each operator record.
- Hello-core uses deterministic fixtures and minimal executor stubs.

## Support Scope
Supported:
- Reproducing verification on Linux hosts with Python 3.12+ using the documented workflow.
- Validating published release artifacts against published checksum files.
Not supported:
- Reproducibility guarantees for modified local trees or dependency changes outside the documented setup.
- Platform-specific packaging/distribution outside repository artifacts.

## Security Contact
- Security contact: `security@astrocytech.com`
- Disclosure policy: `SECURITY.md`

## Artifact Summary
- Conformance results: `evidence/conformance/results/latest.json`
- Conformance report: `evidence/conformance/reports/latest.json`
- Release bundle: `artifacts/bundles/hello-core-bundle.tar.gz`
