# Starter Issue Backlog

Copy these into GitHub Issues with the listed labels.

## 1) Add release verification smoke test in docs examples
Labels: `good first issue`, `docs`, `enhancement`
Acceptance:
- Add one docs snippet showing `glyphser verify hello-core --format json`.
- Include expected PASS fields and evidence file references.

## 2) Add notebook output snapshots
Labels: `good first issue`, `docs`
Acceptance:
- Run `notebooks/quickstart.ipynb` and include saved output cells.
- Ensure outputs show parity/divergence booleans.

## 3) Add CLI error UX tests
Labels: `good first issue`, `tests`
Acceptance:
- Add tests for missing `--model` and unknown `--example` values.
- Ensure clear error messages.

## 4) Add MLflow integration docs section
Labels: `help wanted`, `integration`
Acceptance:
- Document `examples/mlflow_integration.py` in `docs/INTEGRATIONS.md`.
- Include dependency install command.

## 5) Add Jenkins pipeline full example
Labels: `help wanted`, `ci`
Acceptance:
- Add complete Jenkins declarative pipeline under `docs/ci/`.
- Include install + gate + artifact archiving steps.
