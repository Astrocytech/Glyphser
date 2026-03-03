# Release Process

This project uses semantic versioning and Git tags for public releases.

## Release cadence

- Patch (`x.y.Z`): bug fixes and docs-only updates.
- Minor (`x.Y.0`): backward-compatible public API additions.
- Major (`X.0.0`): breaking public API changes.

## Steps

1. Ensure `CHANGELOG.md` and version fields are updated.
2. Create and push a signed tag, for example:
   ```bash
   git tag -s v0.2.0 -m "Glyphser v0.2.0"
   git push origin v0.2.0
   ```
3. GitHub Actions builds release artifacts.
4. PyPI publish runs only when explicitly enabled (`PUBLISH_PYPI=true` repo variable or manual dispatch input).
5. Release workflow also emits:
   - `dist/CHECKSUMS.sha256`
   - `evidence/security/sbom.json`
   - `evidence/security/build_provenance.json`
6. Create GitHub Release notes from `CHANGELOG.md`.

## Required repository settings

- Configure trusted publishing for this repo in PyPI.
- Set repository variable `PUBLISH_PYPI=true` when you are ready to publish from tags.
- Enable GitHub Actions permissions for `id-token: write`.
- Optional: configure GPG signing for checksum/signature publication.
