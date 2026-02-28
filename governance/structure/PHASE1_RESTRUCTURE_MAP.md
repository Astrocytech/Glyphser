# Phase 1 Restructure Map

## Directory Moves
- `docs/business` -> `product/business`
- `docs/product` -> `product/docs`
- `docs/ops` -> `product/ops`
- `docs/site` -> `product/site`
- `docs/security` -> `governance/security`
- `docs/ip` -> `governance/ip`
- `docs/structure` -> `governance/structure`
- `docs/release` -> `distribution/release`

## Root File Moves
- `milestones.txt` -> `governance/roadmap/milestones.txt`
- `ecosystem.md` -> `governance/ecosystem/ecosystem.md`
- `ecosystem-validation-log.md` -> `governance/ecosystem/ecosystem-validation-log.md`
- `ecosystem-registry.yaml` -> `governance/ecosystem/ecosystem-registry.yaml`
- `ecosystem-graph.yaml` -> `governance/ecosystem/ecosystem-graph.yaml`
- `semantic_lint_report.txt` -> `governance/lint/semantic_lint_report.txt`
- `semantic_lint_high_confidence.txt` -> `governance/lint/semantic_lint_high_confidence.txt`
- `portfolio-release-notes-template.md` -> `product/handbook/reports/portfolio-release-notes-template.md`
- `RELEASE_NOTES_v0.1.0.md` -> `distribution/release/RELEASE_NOTES_v0.1.0.md`

Compatibility stubs were left at original paths to avoid CI breakage.
