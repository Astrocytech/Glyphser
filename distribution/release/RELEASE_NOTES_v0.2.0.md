# Release Notes v0.2.0

Release date: 2026-03-03

## Highlights

- Public CLI includes one-command determinism demo:
  - `glyphser verify hello-core`
- Stable/experimental contract is explicitly documented.
- CI now validates Linux/macOS on Python 3.11 and 3.12.
- Coverage artifacts are published from CI.
- Release workflow now emits checksums, SBOM, and provenance artifacts.

## API and CLI

Stable public API remains under `glyphser.public` and top-level `glyphser` re-exports.

Primary user-facing commands:
- `glyphser verify`
- `glyphser snapshot`

## Verification

Local verification entry points:

```bash
make release-check
glyphser verify hello-core --format text --tree
```

## Compatibility

- Python: 3.11, 3.12
- OS in CI matrix: Linux, macOS

## Release Artifacts

- Source distribution and wheel from release workflow (`dist/`)
- `dist/CHECKSUMS.sha256`
- `evidence/security/sbom.json`
- `evidence/security/build_provenance.json`
