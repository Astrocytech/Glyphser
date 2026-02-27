# Glyphser Change Control Playbook
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.ChangeControlPlaybook`
**Purpose (1 sentence):** Define deterministic coding/document change workflow from proposal through merge and release evidence.
**Spec Version:** `Glyphser.Implementation.ChangeControlPlaybook` | 2026-02-19 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Engineering change governance.

---
## 1) Scope
This playbook governs any code or specification change affecting documents, sidecars, schemas, traces, checkpoints, certificates, or operator contracts.

---
## 2) Deterministic Workflow (Normative)
1. Create branch and declare change scope (DocIDs and modules).
2. Apply edits in target docs/code.
3. Run impact analysis:
   - `eqc-es impact --change DOCID@vX.Y.Z`
4. Run lint and wiring verification:
   - `eqc-es validate`
   - `python3 tools/spec_lint.py` (or equivalent contract linter)
5. Update sidecars:
   - `eqc-es regenerate-sidecars`
6. Re-run deterministic hard pass checks.
7. Update `ecosystem-validation-log.md`.
8. Prepare release evidence bundle and merge atomically.

---
## 3) Mandatory Gate Checklist
- No broken markdown references.
- No missing graph edges for discovered references.
- No stale reference edges.
- Registry/graph/node/path parity is complete.
- No layer violations for `IMPORTS/EXTENDS`.
- No undeclared edge type usage.
- Reachability from `CORE-MASTER-001` passes.

---
## 4) Versioning + Migration Rules
- PATCH: wording/trace-neutral and non-breaking contract clarifications.
- MINOR: additive fields/rules with backward compatibility.
- MAJOR: breaking schema/rule/operator behavior changes.
- MAJOR changes require migration note and updated test vectors.

---
## 5) Evidence and Audit Artifacts
Required artifacts for merge:
- updated docs
- updated sidecars (`ecosystem-registry.yaml`, `ecosystem-graph.yaml`)
- validation log entry
- deterministic diff summary

---
## 6) Wiring References
- `ecosystem.md`
- `docs/layer4-implementation/Spec-Lint-Implementation.md`
- `docs/layer4-implementation/Spec-Lint-Rules.md`
- `docs/layer4-implementation/EQC-CI-Policy.md`
- `docs/layer4-implementation/Implementation-Roadmap.md`
- `docs/layer4-implementation/Repo-Layout-and-Interfaces.md`
- `docs/layer3-tests/Test-Plan.md`

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser Change Control Playbook" without altering existing semantics.
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
