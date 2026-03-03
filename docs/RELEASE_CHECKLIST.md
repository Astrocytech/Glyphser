# Release Checklist

This checklist is for cutting a public release (example: `v0.2.0`) and publishing to PyPI.

## 0) Preconditions

- You have push access to `main`.
- GitHub trusted publishing for PyPI is configured.
- CI is green on `main`.
- `CHANGELOG.md` contains release notes for the target version.

## 1) Prepare Version

1. Update version in `pyproject.toml`.
2. Ensure `VERSIONING.md` and compatibility docs are current.
3. Commit changes:

```bash
git add pyproject.toml CHANGELOG.md VERSIONING.md docs/
git commit -m "release: prepare v0.2.0"
git push origin main
```

## 2) Validate Locally

```bash
make release-check
```

## 3) Create and Push Tag

Signed tag (recommended):

```bash
git tag -s v0.2.0 -m "Glyphser v0.2.0"
git push origin v0.2.0
```

Unsigned tag (fallback):

```bash
git tag v0.2.0
git push origin v0.2.0
```

## 4) Verify Release Workflow

- Confirm `.github/workflows/release.yml` ran for `v0.2.0`.
- Confirm build artifacts exist.
- Confirm PyPI publish job succeeded.

## 5) Publish GitHub Release Notes

1. Open GitHub Releases.
2. Create release from tag `v0.2.0`.
3. Paste corresponding `CHANGELOG.md` entry.
4. Link any migration notes.

## 6) Post-Release Checks

```bash
python -m pip install glyphser==0.2.0
python -c "import glyphser; print(glyphser.__all__)"
glyphser --help
```

## 7) Optional: TestPyPI Dry Run

If you maintain a TestPyPI environment, publish there first and verify install.

```bash
python -m pip install --index-url https://test.pypi.org/simple/ glyphser==0.2.0
```
