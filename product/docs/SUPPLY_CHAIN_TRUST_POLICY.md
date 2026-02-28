# Supply Chain Trust Policy

- Dependencies must come from trusted indexes and pinned versions.
- Build provenance artifact required: `reports/security/build_provenance.json`.
- SBOM required: `reports/security/sbom.json`.
- Unsigned or unpinned dependency updates are blocked from GA release.
