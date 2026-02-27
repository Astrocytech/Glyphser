# Glyphser Architecture Decisions Log Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Architecture.DecisionLog`  
**Purpose (1 sentence):** Define deterministic recording, hashing, and lifecycle of architecture decisions (ADR-style) for implementation governance.  
**Spec Version:** `Glyphser.Architecture.DecisionLog` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Architecture governance and traceability.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Architecture.DecisionLog`
- **Purpose (1 sentence):** Deterministic architecture decision contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: prevent undocumented architecture divergence.
### 0.B Reproducibility Contract
- Replayable given `(decision_log_hash, decision_id, context_hash)`.
- `context_hash = SHA-256(CBOR_CANONICAL(context_scope))`, where `context_scope` contains repository root hash, active policy profile id, and affected subsystem set.
### 0.C Numeric Policy
- Decision version and sequence fields are exact integers.
### 0.D Ordering and Tie-Break Policy
- Decision records sorted by `(decision_seq, decision_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Concurrent proposals allowed; accept/reject merge deterministic.
### 0.F Environment and Dependency Policy
- Decisions that affect contracts must link affected contract hashes.
### 0.G Operator Manifest
- `Glyphser.Arch.DecisionCreate`
- `Glyphser.Arch.DecisionSupersede`
- `Glyphser.Arch.DecisionValidateLinks`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `adr/` and `decision_log.cbor` canonical roots.
### 0.I Outputs and Metric Schema
- Outputs: `(decision_report, decision_log_hash)`
- Metrics: `decisions_total`, `superseded_total`
### 0.J Spec Lifecycle Governance
- Decision schema changes are MAJOR.
### 0.K Failure and Error Semantics
- Broken links or duplicate ids fail deterministically.
### 0.L Input/Data Provenance
- Decision records must reference author, context, and affected artifacts.

---
## 2) System Model
### I.A Persistent State
- Architecture decision log.
### I.B Inputs and Hyperparameters
- Decision proposal records and supersession links.

### II.F Decision Record Schema (Normative)
- `decision_record = {`
  - `decision_id:string`,
  - `decision_seq:uint64`,
  - `title:string`,
  - `author:string`,
  - `created_at_utc:string`,
  - `context_scope:map`,
  - `affected_artifacts:array<string>`,
  - `status:enum("PROPOSED","ACCEPTED","REJECTED","SUPERSEDED")`,
  - `supersedes?:string`,
  - `rationale_hash:bytes32`
- `}`
- `created_at_utc` must be ISO 8601 UTC (`YYYY-MM-DDTHH:MM:SSZ`), no fractional seconds.
### I.C Constraints and Feasible Set
- Valid iff decision ids unique and links resolvable.
### I.D Transient Variables
- validation diagnostics and link graph.
### I.E Invariants and Assertions
- Decision history is append-only.

---
## 3) Initialization
1. Load decision log.
2. Validate schema and link graph.
3. Build canonical ordered view.

---
## 4) Operator Manifest
- `Glyphser.Arch.DecisionCreate`
- `Glyphser.Arch.DecisionSupersede`
- `Glyphser.Arch.DecisionValidateLinks`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Arch.DecisionCreate`  
**Signature:** `(decision_record -> decision_id)`  
**Purity class:** IO  
**Determinism:** deterministic.

**Operator:** `Glyphser.Arch.DecisionSupersede`  
**Signature:** `(old_decision_id, new_decision_id -> supersede_record)`  
**Purity class:** IO  
**Determinism:** deterministic.

**Operator:** `Glyphser.Arch.DecisionValidateLinks`  
**Signature:** `(decision_log -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. DecisionCreate
2. DecisionValidateLinks
3. Optional DecisionSupersede
4. Build canonical decision report
5. decision_log_hash <- SHA-256(CBOR_CANONICAL(decision_log))
6. return (decision_report, decision_log_hash)
```

---
## 7) Trace & Metrics
### Logging rule
- Decision operations emit deterministic governance records.
### Trace schema
- `run_header`: decision_log_version
- `iter`: decision_id, action, status
- `run_end`: decision_log_hash
### Metric schema
- `decisions_total`, `superseded_total`
### Comparability guarantee
- Comparable iff same decision set and order.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Unique ids and valid supersession graph.
#### VII.B Operator test vectors (mandatory)
- Create/supersede/link-validation vectors.
#### VII.C Golden traces (mandatory)
- Golden decision-log traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for decision log hash and validation report.
#### VIII.B Allowed refactor categories
- Storage/index refactors preserving log semantics.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of canonical decision log output.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- Decision cursor and log hash.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed operations preserve identical log state.
