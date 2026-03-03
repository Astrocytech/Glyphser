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
3. GitHub Actions builds release artifacts and publishes to PyPI (on trusted publishing).
4. Create GitHub Release notes from `CHANGELOG.md`.

## Required repository settings

- Configure `PYPI_PROJECT` and trusted publisher for this repo.
- Enable GitHub Actions permissions for `id-token: write`.
