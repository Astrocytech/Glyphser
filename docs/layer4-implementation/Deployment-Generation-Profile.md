# Glyphser Deployment Generation Profile
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.DeploymentGenerationProfile`
**Purpose (1 sentence):** Define deterministic generation of deployment bundles, environment manifests, and migration/rollback plans.
**Spec Version:** `Glyphser.Implementation.DeploymentGenerationProfile` | 2026-02-27 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Deployment artifact generation and release readiness.

---
## 1) Output Artifacts (Normative)
- `artifacts/generated/deploy/<profile>/runtime_config.json`
- `artifacts/generated/deploy/<profile>/policy_bindings.json`
- `artifacts/generated/deploy/<profile>/bundle_manifest.json`
- `artifacts/generated/deploy/env_manifest.json`
- `artifacts/generated/deploy/migration_plan.json`

Profiles: `managed`, `confidential`, `regulated`.

---
## 2) Deterministic Defaults (Normative)
- All deployment outputs are deterministic functions of template inputs and the current catalog manifest.
- Execution mode for each bundle equals the profile name.
- Logging defaults to `INFO` with trace sidecar enabled.
- Checkpointing enabled with `interval_steps=1` for reference deployments.

---
## 3) Migration and Rollback (Normative)
- Migration plan compares current and previous catalog digest hashes.
- When the digest changes: action is rebuild artifacts; rollback restores previous manifest and regenerates.
- When unchanged: action is a no-op, rollback is no-op.

---
## 4) Validation (Normative)
- Bundle manifests must include `profile` and a `bundle_hash` over artifacts.
- Validation must fail if any required files are missing or the profile is mismatched.
- CI must run the deployment pipeline in deterministic order.

---
## 5) Local Entry Points
- Generate bundles: `python tools/deploy/generate_bundle.py`
- Generate env manifest: `python tools/deploy/generate_env_manifest.py`
- Generate migration plan: `python tools/deploy/generate_migration_plan.py`
- Validate profiles: `python tools/deploy/validate_profile.py`
- Full pipeline: `python tools/deploy/run_deployment_pipeline.py`
