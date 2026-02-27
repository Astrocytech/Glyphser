# Glyphser EQC CI Policy
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.EQCCIPolicy`
**Purpose (1 sentence):** Define deterministic CI gate policy that maps EQC lint/test outcomes to merge and release decisions.
**Spec Version:** `Glyphser.Implementation.EQCCIPolicy` | 2026-02-19 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** CI/CD governance for EQC conformance.

---
## 1) Pipeline Stages (Normative)
1. `stage_lint`
2. `stage_contract_sync`
3. `stage_conformance`
4. `stage_replay`
5. `stage_release_gates`

Stage order is fixed and deterministic.

---
## 2) Mandatory Commands
- `eqc-es validate`
- `eqc-es impact --change DOCID@vX.Y.Z`
- `eqc-es regenerate-sidecars`
- `python3 tools/spec_lint.py`

---
## 3) Gate Mapping Rules
- Any BLOCKER lint finding: `merge=DENY`.
- Missing graph/reference parity: `merge=DENY`.
- Layer or edge-type violation: `merge=DENY`.
- Conformance or replay gate failure: `release=DENY`.
- Warnings only: `merge=ALLOW_WITH_NOTICE`.

---
## 4) Deterministic Verdict Contract
`ci_verdict_hash = SHA-256(CBOR_CANONICAL([pipeline_id, [commit_hash, stage_outcomes, lint_verdict, conformance_verdict, replay_verdict]]))`

`ci_verdict_hash` is logged in release evidence and validation logs.

---
## 5) Wiring References
- `docs/layer4-implementation/Build-and-CI-Matrix.md`
- `docs/layer4-implementation/Spec-Lint-Implementation.md`
- `docs/layer4-implementation/Spec-Lint-Rules.md`
- `docs/layer4-implementation/Change-Control-Playbook.md`
- `docs/layer3-tests/Test-Plan.md`
- `ecosystem.md`

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser EQC CI Policy" without altering existing semantics.
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
