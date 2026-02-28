# Phase 2 Artifact Consolidation

Status: COMPLETE (CI-safe, compatibility preserved)

## Canonical Paths

- `artifacts/inputs/fixtures/` (was `fixtures/`)
- `artifacts/inputs/vectors/` (was `vectors/`)
- `artifacts/expected/goldens/` (was `goldens/`)
- `artifacts/generated/` (was `generated/`)
- `artifacts/bundles/` (was `dist/`)
- `evidence/` (was `reports/`)
- `evidence/conformance/reports/` (was `conformance/reports/`)
- `evidence/conformance/results/` (was `conformance/results/`)

## Compatibility Layer

Legacy paths are preserved as symlinks so current tests/tools/workflows continue to run unchanged:

- `fixtures -> artifacts/inputs/fixtures`
- `vectors -> artifacts/inputs/vectors`
- `goldens -> artifacts/expected/goldens`
- `generated -> artifacts/generated`
- `dist -> artifacts/bundles`
- `reports -> evidence`
- `conformance/reports -> ../evidence/conformance/reports`
- `conformance/results -> ../evidence/conformance/results`

## Validation

- `python3 -m pytest -q` -> PASS
- `python3 tools/push_button.py` -> PASS

## Notes

- This preserves deterministic single-source artifact storage while avoiding immediate path breakage.
- Next step (optional): remove symlink compatibility after all references are upgraded to canonical paths.
