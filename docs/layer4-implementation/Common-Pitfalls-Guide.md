# Glyphser Common Pitfalls and How to Avoid Them
**Spec Version:** v1.0.0 | 2026-02-20 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**EQC Compliance:** Informational companion; normative behavior remains in contract docs.

## 1) Pitfall: Mixing Non-Canonical Serialization
- Symptom: hash mismatches for apparently identical objects.
- Why it happens: non-canonical map ordering or string encoding drift.
- Avoidance: always use canonical CBOR paths defined in layer1/layer2 contracts.

## 2) Pitfall: Reusing Tensor State Outside TMMU Rules
- Symptom: replay divergence in backward/optimizer paths.
- Why it happens: hidden aliasing and non-declared memory lifecycle.
- Avoidance: obey TMMU allocation/liveness contracts and explicit ownership rules.

## 3) Pitfall: Treating Timing as Deterministic Verdict Input
- Symptom: flaky gate outcomes near thresholds.
- Why it happens: wall-clock metrics vary naturally.
- Avoidance: keep timing informational unless contractually thresholded with explicit tolerance policy.

## 4) Pitfall: Incomplete Evidence Linkage
- Symptom: certificate validation failure despite successful run.
- Why it happens: missing hash-link fields in evidence bundle.
- Avoidance: assemble evidence only through release evidence assembler contract.

## 5) Pitfall: Skipping Replay Before Promotion
- Symptom: production-only nondeterminism discovered late.
- Why it happens: missing deterministic replay check in release workflow.
- Avoidance: make replay conformance mandatory before release gate evaluation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser Common Pitfalls and How to Avoid Them" without altering existing semantics.
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
