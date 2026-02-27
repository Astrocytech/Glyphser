# Offers (Fixed Scope)

Status: DRAFT

See also: `docs/business/DELIVERABLES_LIST.md`

## Offer 1: 2-hour Conformance Audit
- Scope: run conformance suite, verify artifacts, review determinism report against published contracts.
- Inputs required: project repo or release bundle, build/verify instructions, target environment notes.
- Deliverables: audit summary + PASS/FAIL evidence bundle + issue list (if any).
- Fixed timebox: 2 hours of analysis.
- Excludes: implementation changes, custom feature work, bespoke tooling.
- Price: TBD
- Turnaround: TBD

## Offer 2: Verifier-in-CI Integration Pack
- Scope: add conformance run/verify/report to CI with deterministic verification step.
- Inputs required: CI system details, repo access, existing pipeline context.
- Deliverables: CI workflow updates + runbook + reproducibility checklist.
- Fixed scope: one primary CI pipeline, one target runner environment.
- Excludes: non-Glyphser tooling integration beyond CI, infra provisioning.
- Price: TBD
- Turnaround: TBD
