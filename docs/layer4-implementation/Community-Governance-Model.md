# Glyphser Community Governance Model
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Governance.CommunityModel`  
**Purpose (1 sentence):** Define open governance and contribution processes for deterministic evolution of Glyphser specifications and tooling.  
**Spec Version:** `Glyphser.Governance.CommunityModel` | 2026-02-20 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`


---
## 1) RFC Process
- Stages:
  - draft,
  - review,
  - final comment period,
  - acceptance/rejection.
- Mandatory RFC evidence:
  - migration impact,
  - compatibility impact,
  - test vectors,
  - release-gate implications.

## 2) Technical Steering Committee Charter
- Rotating representatives from major contributor organizations.
- Responsibilities:
  - resolve disputes,
  - approve MAJOR releases,
  - arbitrate compatibility policy conflicts.

## 3) Versioning and Backport Policy
- Major versions supported for 2 years.
- Critical security fixes backported to last 2 major lines.
- Minor lines receive bugfixes until superseded by 2 newer minors.

## 4) Contribution Ladder
- issue reporter -> doc contributor -> contract maintainer -> reviewer -> steward.
- Promotion criteria are deterministic and evidence-based.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser Community Governance Model" without altering existing semantics.
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
