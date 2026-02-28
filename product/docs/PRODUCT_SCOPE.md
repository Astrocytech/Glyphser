# Product Scope (Milestone 17)

Status: APPROVED FOR IMPLEMENTATION
Version: 0.1
Owner: Glyphser maintainers

## Purpose
Define MVP scope, non-goals, target users, support boundaries, and acceptance metrics for turning Glyphser from reference stack into a production product track.

## Product Definition
Glyphser is a deterministic execution and verification platform that produces reproducible evidence artifacts (conformance reports, bundle hashes, replay evidence) across supported runtime profiles.

## Target Personas
- Platform engineer integrating deterministic verification into CI/CD and release pipelines.
- ML systems engineer validating model/data execution evidence for audits and replay.
- Security/compliance reviewer validating release integrity and chain-of-custody artifacts.

## Primary User Journeys
- First 30 minutes:
- Clone repo, create virtual environment, run `python tools/verify_release.py`, confirm `VERIFY_RELEASE: PASS`.
- Review release notes hash table and verify signed checksum file.
- Execute profile-specific quickstart for local or production profile.
- Ongoing usage:
- Submit run workload through product API/CLI (Milestone 18+).
- Retrieve run status, evidence package, and replay outcome.
- Audit run and release artifacts against published checksums and policy docs.

## MVP In-Scope Use Cases
- Deterministic local verification and reproducibility evidence generation.
- Signed release artifact verification for external users.
- Profile-based operational guidance (local dev, single-node production, regulated multi-node).
- Deterministic replay and conformance validation on supported environments.

## Explicit Non-Goals (MVP)
- Full multi-region active-active runtime orchestration.
- Real-time interactive inference serving at internet-scale.
- Unbounded model classes without declared profile limits.
- Automatic third-party dependency trust attestation outside declared supply-chain policy.

## Supported Environments (MVP)
- Linux x86_64 hosts with Python 3.12+ (primary supported baseline).
- WSL-based Linux runtime for development validation (best effort unless profile marks otherwise).
- Containerized runtime in staging/production under Milestone 21 deployment rules.

## Commercial Model Assumptions
- Primary model: self-hosted deployment by customer/operator.
- Managed service model: out of scope for MVP; may be introduced post-GA with separate controls.

## Tenancy and Isolation
- Local Dev profile: single-tenant, local isolation only.
- Single-Node Production profile: single-tenant with process and storage isolation.
- Multi-Node Regulated profile: multi-tenant capable only with strict RBAC, audit trails, and namespace isolation.

## Data Classification and Compliance Boundary
- Public: documentation and published release metadata.
- Internal: operational telemetry, CI evidence, non-sensitive configs.
- Sensitive/regulated: customer workloads, checkpoints, and evidence with policy restrictions.
- Compliance boundary: profile-defined; regulated profile requires explicit controls and auditability.

## Data Lifecycle Policy (Baseline)
- Retention: profile-specific minimum and maximum windows defined in `RUNTIME_PROFILES.md`.
- Deletion: explicit delete workflow with evidence of deletion action.
- Export: deterministic export format for evidence artifacts and profile metadata.

## Internationalization/Localization
- MVP scope: English-language interfaces and documentation only.
- Non-goal: full localization and translated operational artifacts in MVP.

## Time Synchronization Baseline
- All profiles require synchronized clocks.
- Baseline tolerance: host clock drift must remain within profile threshold (see profile matrix).
- Timestamps used in evidence and audit logs must be traceable to synchronized system time.

## Product Success Metrics (Milestone 17 Acceptance)
- Adoption:
- At least 3 internal teams or external evaluators complete first-run verification flow.
- Reliability:
- Deterministic verify command success rate >= 99% on supported environments.
- Support burden:
- Median time-to-first-success <= 30 minutes using published docs.
- Critical onboarding issues unresolved at milestone close: 0.

## Scope Acceptance Checklist
- MVP use cases documented with explicit non-goals.
- Target personas and first 30-minute journey documented.
- Supported environments and tenancy model documented.
- Data classification/lifecycle and compliance boundaries documented.
- Success metrics defined and review-approved.

