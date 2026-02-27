# Glyphser Security Case Template
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Security.SecurityCaseTemplate`
**Purpose (1 sentence):** Provide a deterministic, hash-addressed template for auditor-ready security case submissions.
**Spec Version:** `Glyphser.Security.SecurityCaseTemplate` | 2026-02-21 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Security.SecurityCaseTemplate`
- **Purpose (1 sentence):** Deterministic security-case packaging template.
- **Spec Version:** `Glyphser.Security.SecurityCaseTemplate` | 2026-02-21 | Authors: Olejar Damir
- **Domain / Problem Class:** audit-ready control mapping and evidence binding.
### 0.A Objective Semantics
- Convert threat controls into verifiable evidence obligations.
### 0.B Reproducibility Contract
- Replayable given `(security_case_input_set, control_catalog_hash, evidence_refs)`.
### 0.C Numeric Policy
- N/A.
### 0.D Ordering and Tie-Break Policy
- Control entries sorted by `control_id`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Control checks parallelizable; verdict aggregation deterministic fail-dominant.
### 0.F Environment and Dependency Policy
- Required evidence must be content-addressed and canonical.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Product.EmitSecurityCase`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `security_case/<profile>/<release_id>/`.
### 0.I Outputs and Metric Schema
- Outputs: `(security_case_report, security_case_hash)`.
### 0.J Spec Lifecycle Governance
- Template fields are MAJOR-governed.
### 0.K Failure and Error Semantics
- Missing required evidence path is deterministic failure.
### 0.L Input/Data Provenance
- Inputs from threat model, policy transcripts, execution certificate, release evidence.

## 2) Template Schema (Normative)
- `security_case` object must contain:
  - `profile_id` (`core|enterprise|regulated`)
  - `assets[]`
  - `trust_boundaries[]`
  - `attacker_capabilities[]`
  - `controls[]` with fields:
    - `control_id`
    - `mitigation`
    - `evidence_locations[]`
    - `verification_procedure_ref`
    - `verdict`

## 3) Identity Rule (Normative)
- `security_case_hash = SHA-256(CBOR_CANONICAL(["security_case", security_case]))`.

## 4) References
- `docs/layer4-implementation/Threat-Model-and-Control-Crosswalk.md`
- `docs/layer2-specs/Security-Compliance-Profile.md`
- `docs/layer4-implementation/Evidence-Catalog.md`

## 6) Procedure
```text
1. Build control entries from threat model crosswalk.
2. Resolve evidence locations and run verification procedures.
3. Emit control verdicts and security_case report.
4. Compute security_case_hash.
```
