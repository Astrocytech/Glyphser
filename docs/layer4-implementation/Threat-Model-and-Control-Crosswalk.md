# Glyphser Threat Model and Control Crosswalk
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Security.ThreatModelCrosswalk`  
**Purpose (1 sentence):** Formalize attacker model, trust boundaries, and control-to-evidence mapping for auditor-ready verification.  
**Spec Version:** `Glyphser.Security.ThreatModelCrosswalk` | 2026-02-20 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`


---
## 1) Threat Model Scope
- Assets: manifests, model state, trace, checkpoints, certificates, policy bundles, keys.
- Trust boundaries: client, daemon, storage backend, backend driver, attestation service, verifier.
- Attacker capabilities: tampering, replay, unauthorized access, partial storage corruption, network partition manipulation.

## 2) Control Mapping
- Each control entry MUST define:
  - `control_id`
  - `threat_ids`
  - `required_mitigations`
  - `evidence_fields`
  - `verification_procedure`

## 3) Mode-Specific Obligations
- `core`: baseline authz + evidence integrity.
- `enterprise`: adds operational governance controls.
- `regulated`: adds attestation/revocation/control-crosswalk completeness requirements.

## 4) Verification Output
- `control_crosswalk_report`
- `control_crosswalk_hash`

## 5) Related Contracts
- `docs/layer2-specs/Security-Compliance-Profile.md`
- `docs/layer2-specs/Execution-Certificate.md`

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser Threat Model and Control Crosswalk" without altering existing semantics.
- **Spec Version:** `Glyphser.Structural.Addendum` | 2026-02-20 | Authors: ML2ML
- **Domain / Problem Class:** Documentation governance and structural conformance.
### 0.Z EQC Mandatory Declarations Addendum
- This document inherits deterministic, numeric, and failure policies from its referenced normative contracts unless explicitly overridden.

---
## 6) Procedure
```text
1. Read and apply this document together with its referenced normative contracts.
2. Preserve deterministic ordering and evidence linkage requirements declared by those contracts.
3. Emit deterministic documentation compliance record for governance tracking.
```

## 6) Security Case Template Reference (Normative)
- `docs/layer4-implementation/Security-Case-Template.md` defines hash-addressed auditor package structure for this crosswalk.
