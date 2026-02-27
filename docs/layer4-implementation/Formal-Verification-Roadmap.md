# Glyphser Formal Verification Roadmap
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Verification.FormalRoadmap`  
**Purpose (1 sentence):** Define mechanized proof targets for critical correctness and determinism properties.  
**Spec Version:** `Glyphser.Verification.FormalRoadmap` | 2026-02-20 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`


---
## 1) Priority Proof Targets
### I.A TMMU Slot Assignment Optimality
- Target: prove interval-graph coloring optimality for logical slot assignment.
- Scope: `TMMU.AssignLogicalSlots` and related liveness assumptions.

### I.B Privacy Accountant Correctness
- Target: prove PLD/Moments accountant compositional correctness and numerical stability bounds.
- Scope: DP accountant operators and stable floating-point/approximation constraints.

### I.C IR Type/Shape Safety
- Target: mechanized typing/shape discipline proving absence of runtime shape mismatch for well-typed IR.
- Scope: UML_Model_IR typing rules and executor preconditions.

---
## 2) Proof Artifact Requirements
- Every proof package MUST include:
  - formal statement,
  - assumptions,
  - mechanized proof artifact reference,
  - executable extraction/test witness,
  - proof bundle hash.

---
## 3) Governance
- Proof regressions are release blockers for `regulated` profile when proof-marked contracts are modified.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser Formal Verification Roadmap" without altering existing semantics.
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
