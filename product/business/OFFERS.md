# Offers (Fixed Scope)

Status: ACTIVE DRAFT

See also: `product/business/DELIVERABLES_LIST.md`

All offers are fixed-scope and evidence-first. Final commercial terms are confirmed in writing before work begins.

## Offer 1: 2-hour Conformance Audit
- Scope: run conformance suite, verify artifacts, review determinism report against published contracts.
- Inputs required: project repo or release bundle, build/verify instructions, target environment notes.
- Deliverables: audit summary + PASS/FAIL evidence bundle + issue list (if any).
- Fixed timebox: 2 hours of analysis.
- Excludes: implementation changes, custom feature work, bespoke tooling.
- Pricing model: fixed fee per audit session, agreed at intake.
- Standard turnaround: within 2 business days after all required inputs are received.
- Best fit for: teams that need an independent technical verification snapshot quickly.

## Offer 2: Verifier-in-CI Integration Pack
- Scope: add conformance run/verify/report to CI with deterministic verification step.
- Inputs required: CI system details, repo access, existing pipeline context.
- Deliverables: CI workflow updates + runbook + reproducibility checklist.
- Fixed scope: one primary CI pipeline, one target runner environment.
- Excludes: non-Glyphser tooling integration beyond CI, infra provisioning.
- Pricing model: fixed package fee for one CI lane and one environment.
- Standard turnaround: 5-10 business days, depending on CI access and review latency.
- Best fit for: teams moving from manual verification to repeatable CI enforcement.

## Engagement Rules
- Work starts only after scope, inputs, and acceptance criteria are written and approved.
- Out-of-scope requests are moved to a separate follow-on statement of work.
- Client data and artifacts are handled under least-access principles.

## Acceptance Criteria
- Offer 1 is complete when the report and evidence bundle are delivered with a clear PASS/FAIL verdict.
- Offer 2 is complete when CI runs the agreed verification path and the runbook is delivered.

## Commercial Notes
- Payment terms, invoicing details, and exact fees are defined per engagement.
- Taxes, payment processor fees, and jurisdictional requirements are handled per signed agreement.
