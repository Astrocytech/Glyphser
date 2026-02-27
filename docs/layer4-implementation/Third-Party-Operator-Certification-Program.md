# Glyphser Third-Party Operator Certification Program
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Marketplace.OperatorCertification`  
**Purpose (1 sentence):** Define deterministic lifecycle for third-party operator development, conformance certification, and publication.  
**Spec Version:** `Glyphser.Marketplace.OperatorCertification` | 2026-02-20 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`


---
## 1) Program Levels
- `Level 1`: local conformance pass.
- `Level 2`: profile conformance pass (`core` / `enterprise`).
- `Level 3`: regulated-grade certification with full evidence package.

## 2) Required Inputs
- operator registry entry,
- canonical signatures/digest refs,
- test vectors,
- conformance harness reports,
- security declaration,
- SBOM hash.

## 3) Certification Evidence Package Format
- `operator_package_manifest.json`
- `operator_contract_bundle.cbor`
- `conformance_package.cbor`
- `security_statement.json`
- `sbom.json`
- `certification_verdict.json`

## 4) Publication Rules
- Only deterministic, hash-addressed, and signature-verified packages may be published.
- Certified package must include sunset/deprecation metadata.

## 5) Revocation and Renewal
- Revocation emits signed revocation record with reason code.
- Renewal requires rerun of profile-appropriate conformance suites.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser Third-Party Operator Certification Program" without altering existing semantics.
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
