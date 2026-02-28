# GA Compatibility Guarantees

- API contract is semver-governed (`specs/contracts/openapi_public_api_v1.yaml`).
- Replay/state schemas remain backward-compatible within GA minor versions.
- Evidence artifact filenames and checksum workflow remain stable for GA line.
- Breaking changes require major version bump and migration documentation.
