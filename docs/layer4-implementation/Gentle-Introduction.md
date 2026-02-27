# Glyphser Gentle Introduction
**Spec Version:** v1.0.0 | 2026-02-20 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**EQC Compliance:** Informational companion, non-authoritative for contract semantics.

**Purpose (1 sentence):** Provide a beginner-friendly conceptual path before deep contract details.

## 1) What Glyphser Is
- A deterministic execution contract for ML systems.
- Focuses on reproducibility, auditability, and controlled evolution.

## 2) Mental Model
- Manifest defines intent.
- Operators execute deterministically.
- Trace records what happened.
- Checkpoint captures recoverable state.
- Certificate proves execution claims.

## 3) First Learning Path
1. Read `Reference-Stack-Minimal.md`.
2. Run hello world example.
3. Inspect trace and certificate.
4. Learn replay determinism and gate policies.

## 4) What to Read Next
- `docs/layer2-specs/Glyphser-Kernel-v3.22-OS.md`
- `docs/layer2-specs/Execution-Certificate.md`
- `docs/layer3-tests/Conformance-Harness-Guide.md`

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser Gentle Introduction" without altering existing semantics.
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
