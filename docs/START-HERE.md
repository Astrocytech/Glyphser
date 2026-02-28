# Glyphser Start Here (Core Profile)
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Onboarding.StartHereCore`  
**Purpose (1 sentence):** Provide the minimum deterministic onboarding path for first successful Core profile execution.  
**Spec Version:** `Glyphser.Onboarding.StartHereCore` | 2026-02-21 | Authors: Olejar Damir  
**Normativity Legend:** `specs/layers/L1-foundation/Normativity-Legend.md`

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Onboarding.StartHereCore`
- **Purpose (1 sentence):** Deterministic onboarding contract for Core profile first run.
- **Spec Version:** `Glyphser.Onboarding.StartHereCore` | 2026-02-21 | Authors: Olejar Damir
- **Domain / Problem Class:** onboarding and first-run determinism verification.

### 0.A Objective Semantics
- Ensure a new user can deterministically produce core evidence identities on first successful run.

### 0.B Documentation Routing
- Use `docs/` for repository navigation and first-run verification.
- Use `specs/` for normative technical behavior and schema/contract truth.
- Use `product/handbook/` for product-facing operational policy and guides.
- Use `governance/` for project process, structure policy, and roadmap controls.

---
## 2) Scope (Normative)
- This document defines the minimal file set and expected deterministic identities for first-run Core profile validation.
- Core profile target: single-node, one backend adapter, one artifact store adapter, default trace policy.

---
## 3) Required File Set (Normative)
- `specs/layers/L4-implementation/Reference-Stack-Minimal.md`
- `specs/layers/L4-implementation/Hello-World-End-to-End-Example.md`
- `specs/layers/L2-specs/Glyphser-Kernel-v3.22-OS.md`
- `specs/layers/L2-specs/Run-Commit-WAL.md`
- `specs/layers/L2-specs/Trace-Sidecar.md`
- `specs/layers/L2-specs/Execution-Certificate.md`
- `artifacts/inputs/fixtures/hello-core/manifest.core.yaml`
- `specs/examples/hello-core/hello-core-golden.json`

---
## 4) Expected Deterministic Outputs (Normative)
- First successful run MUST emit:
  - `trace_final_hash`
  - `certificate_hash`
  - `interface_hash`
- The expected values are sourced from `specs/examples/hello-core/hello-core-golden.json`.
- Any mismatch is a deterministic onboarding failure for this profile fixture.

## 6) Procedure
```text
1. Load Core fixture manifest: artifacts/inputs/fixtures/hello-core/manifest.core.yaml.
2. Execute minimal reference stack workflow (WAL -> trace -> checkpoint -> certificate -> replay check).
3. Compute trace_final_hash, certificate_hash, interface_hash via canonical CBOR hashing rules.
4. Compare emitted values against specs/examples/hello-core/hello-core-golden.json.
5. Emit deterministic onboarding verdict.
```

---
## 7) Golden Demo Evidence Bundle (Normative)
- Bundle identity:
  - `hello_core_demo_bundle_hash = SHA-256(CBOR_CANONICAL(["hello_core_demo", [fixture_ids, expected_identities]]))`.
- Required fixture bindings:
  - `manifest_fixture_ref = artifacts/inputs/fixtures/hello-core/manifest.core.yaml`
  - `fixture_manifest_ref = artifacts/inputs/fixtures/hello-core/fixture-manifest.json`
  - `golden_identity_ref = artifacts/expected/goldens/hello-core/golden-identities.json`
  - `golden_manifest_ref = artifacts/expected/goldens/hello-core/golden-manifest.json`
  - `catalog_manifest_ref = specs/contracts/catalog-manifest.json`
- Required verifier refs:
  - `specs/layers/L4-implementation/Evidence-Catalog.md`
  - `specs/layers/L4-implementation/Determinism-Audit-Playbook.md`
  - `tooling/docs/verify_doc_artifacts.py`

## 8) Artifact Verification Command (Normative)
- Verification command:
  - `python tooling/docs/verify_doc_artifacts.py`
- Result policy:
  - PASS is required before profile onboarding can be considered complete.
