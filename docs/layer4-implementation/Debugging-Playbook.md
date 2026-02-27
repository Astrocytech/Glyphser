# Glyphser Debugging Playbook Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.DebuggingPlaybook`  
**Purpose (1 sentence):** Define deterministic debugging workflows for replay divergences, hash mismatches, and contract failures.  
**Spec Version:** `Glyphser.Implementation.DebuggingPlaybook` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Incident triage and deterministic diagnostics.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.DebuggingPlaybook`
- **Purpose (1 sentence):** Deterministic debugging/triage contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: minimize time-to-root-cause with reproducible diagnostics.
### 0.B Reproducibility Contract
- Replayable given `(replay_token, trace_final_hash, checkpoint_hash, env_manifest_hash)`.
### 0.C Numeric Policy
- Diff comparisons use declared E0/E1 profile only.
### 0.D Ordering and Tie-Break Policy
- Triage steps follow fixed deterministic order.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel probes allowed; final diagnosis path deterministic.
### 0.F Environment and Dependency Policy
- Debugging must preserve original artifact identities.
### 0.G Operator Manifest
- `Glyphser.Debug.LoadEvidence`
- `Glyphser.Debug.FindFirstDivergence`
- `Glyphser.Debug.ClassifyRootCause`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Debug.*`
### 0.I Outputs and Metric Schema
- Outputs: `(debug_report, root_cause_class)`
- Metrics: `divergence_step`, `signals_collected`
### 0.J Spec Lifecycle Governance
- Root-cause class taxonomy changes are MAJOR.
### 0.K Failure and Error Semantics
- Missing evidence yields deterministic diagnostic failure.
### 0.L Input/Data Provenance
- All debug conclusions must cite evidence hashes.

---
## 2) System Model
### I.A Persistent State
- Debug taxonomy and known failure signatures.
### I.B Inputs and Hyperparameters
- Trace/checkpoint/certificate/WAL evidence, replay mode.
### I.C Constraints and Feasible Set
- Valid iff evidence tuple is complete and hash-consistent.
### I.D Transient Variables
- divergence diff maps and ranked suspects.
### I.E Invariants and Assertions
- First divergence location must be deterministic.

---
## 3) Initialization
1. Load evidence tuple.
2. Validate hash/cert coherence.
3. Select replay comparator profile.

---
## 4) Operator Manifest
- `Glyphser.Debug.LoadEvidence`
- `Glyphser.Debug.FindFirstDivergence`
- `Glyphser.Debug.ClassifyRootCause`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Debug.LoadEvidence`  
**Signature:** `(run_id -> evidence_bundle)`  
**Purity class:** IO  
**Determinism:** deterministic.

**Operator:** `Glyphser.Debug.FindFirstDivergence`  
**Signature:** `(trace_a, trace_b, compare_profile -> divergence_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

**Operator:** `Glyphser.Debug.ClassifyRootCause`  
**Signature:** `(divergence_report, evidence_bundle -> root_cause_class, debug_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. LoadEvidence
2. FindFirstDivergence
3. ClassifyRootCause
4. Emit debug_report
```

---
## 7) Trace & Metrics
### Logging rule
- Debug runs emit deterministic triage events.
### Trace schema
- `run_header`: debug_profile, source_run_id
- `iter`: step_id, check_id, status
- `run_end`: root_cause_class, debug_report_hash
### Metric schema
- `divergence_step`, `signals_collected`
### Comparability guarantee
- Comparable iff same evidence and profile.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Every conclusion references committed evidence hashes.
#### VII.B Operator test vectors (mandatory)
- Divergence and root-cause classification fixtures.
#### VII.C Golden traces (mandatory)
- Golden debug triage traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for divergence location and root cause class.
#### VIII.B Allowed refactor categories
- Tooling implementation changes preserving verdicts.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of debug reports on fixed evidence.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- Triage cursor and intermediate diagnosis state.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed debug session must preserve final diagnosis.
