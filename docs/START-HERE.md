# Glyphser Start Here (Core Profile)
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Onboarding.StartHereCore`  
**Purpose (1 sentence):** Provide the minimum deterministic onboarding path for first successful Core profile execution.  
**Spec Version:** `Glyphser.Onboarding.StartHereCore` | 2026-02-21 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Onboarding.StartHereCore`
- **Purpose (1 sentence):** Deterministic onboarding contract for Core profile first run.
- **Spec Version:** `Glyphser.Onboarding.StartHereCore` | 2026-02-21 | Authors: Olejar Damir
- **Domain / Problem Class:** onboarding and first-run determinism verification.

### 0.A Objective Semantics
- Ensure a new user can deterministically produce core evidence identities on first successful run.

---
## 2) Scope (Normative)
- This document defines the minimal file set and expected deterministic identities for first-run Core profile validation.
- Core profile target: single-node, one backend adapter, one artifact store adapter, default trace policy.

---
## 3) Required File Set (Normative)
- `docs/layer4-implementation/Reference-Stack-Minimal.md`
- `docs/layer4-implementation/Hello-World-End-to-End-Example.md`
- `docs/layer2-specs/Glyphser-Kernel-v3.22-OS.md`
- `docs/layer2-specs/Run-Commit-WAL.md`
- `docs/layer2-specs/Trace-Sidecar.md`
- `docs/layer2-specs/Execution-Certificate.md`
- `docs/examples/hello-core/manifest.core.yaml`
- `docs/examples/hello-core/hello-core-golden.json`

---
## 4) Expected Deterministic Outputs (Normative)
- First successful run MUST emit:
  - `trace_final_hash`
  - `certificate_hash`
  - `interface_hash`
- The expected values are sourced from `docs/examples/hello-core/hello-core-golden.json`.
- Any mismatch is a deterministic onboarding failure for this profile fixture.

## 6) Procedure
```text
1. Load Core fixture manifest: docs/examples/hello-core/manifest.core.yaml.
2. Execute minimal reference stack workflow (WAL -> trace -> checkpoint -> certificate -> replay check).
3. Compute trace_final_hash, certificate_hash, interface_hash via canonical CBOR hashing rules.
4. Compare emitted values against docs/examples/hello-core/hello-core-golden.json.
5. Emit deterministic onboarding verdict.
```

---
## 7) Golden Demo Evidence Bundle (Normative)
- Bundle identity:
  - `hello_core_demo_bundle_hash = SHA-256(CBOR_CANONICAL(["hello_core_demo", [fixture_ids, expected_identities]]))`.
- Required fixture bindings:
  - `manifest_fixture_ref = fixtures/hello-core/manifest.core.yaml`
  - `fixture_manifest_ref = fixtures/hello-core/fixture-manifest.json`
  - `golden_identity_ref = goldens/hello-core/golden-identities.json`
  - `golden_manifest_ref = goldens/hello-core/golden-manifest.json`
  - `catalog_manifest_ref = contracts/catalog-manifest.json`
- Required verifier refs:
  - `docs/layer4-implementation/Evidence-Catalog.md`
  - `docs/layer4-implementation/Determinism-Audit-Playbook.md`
  - `tools/verify_doc_artifacts.py`

## 8) Artifact Verification Command (Normative)
- Verification command:
  - `python tools/verify_doc_artifacts.py`
- Result policy:
  - PASS is required before profile onboarding can be considered complete.
