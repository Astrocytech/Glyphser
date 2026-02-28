# Phase 2 Artifact Consolidation

Status: COMPLETE (CI-safe, compatibility preserved)

## Canonical Paths

- `artifacts/inputs/fixtures/` (was `artifacts/inputs/fixtures/`)
- `artifacts/inputs/conformance/` (was `artifacts/inputs/conformance/`)
- `artifacts/expected/goldens/` (was `artifacts/expected/goldens/`)
- `artifacts/artifacts/generated/` (was `artifacts/generated/`)
- `artifacts/bundles/` (was `artifacts/bundles/`)
- `evidence/` (was `evidence/`)
- `evidence/conformance/reports/` (was `evidence/conformance/reports/`)
- `evidence/conformance/results/` (was `evidence/conformance/results/`)

## Compatibility Layer

Legacy paths are preserved as symlinks so current tests/tooling/workflows continue to run unchanged:

- `fixtures -> artifacts/inputs/fixtures`
- `vectors -> artifacts/inputs/conformance`
- `goldens -> artifacts/expected/goldens`
- `generated -> artifacts/generated`
- `dist -> artifacts/bundles`
- `reports -> evidence`
- `conformance/reports -> ../evidence/conformance/reports`
- `conformance/results -> ../evidence/conformance/results`

## Validation

- `python3 -m pytest -q` -> PASS
- `python3 tooling/commands/push_button.py` -> PASS

## Notes

- This preserves deterministic single-source artifact storage while avoiding immediate path breakage.
- Next step (optional): remove symlink compatibility after all references are upgraded to canonical paths.
