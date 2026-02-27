# Glyphser Build and CI Matrix Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.BuildCIMatrix`  
**Purpose (1 sentence):** Define deterministic build targets, CI gates, and matrix validation rules for Glyphser implementation.  
**Spec Version:** `Glyphser.Implementation.BuildCIMatrix` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Build orchestration and CI gate governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.BuildCIMatrix`
- **Purpose (1 sentence):** Deterministic CI matrix contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: eliminate non-deterministic build/test outcomes.
### 0.B Reproducibility Contract
- Replayable given `(commit_hash, lockfile_hash, matrix_hash, env_manifest_hash)`.
### 0.C Numeric Policy
- Gate thresholds use binary64/integer deterministic comparisons.
### 0.D Ordering and Tie-Break Policy
- Matrix jobs ordered by `(profile, backend, mode)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Jobs run in parallel; gate verdict reduction order fixed.
### 0.F Environment and Dependency Policy
- CI workers must satisfy `docs/layer1-foundation/Environment-Manifest.md` and lock policy.
### 0.G Operator Manifest
- `Glyphser.CI.RunBuild`
- `Glyphser.CI.RunTestSuite`
- `Glyphser.CI.EvaluateGates`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.CI.*`
### 0.I Outputs and Metric Schema
- Outputs: `(ci_report, gate_verdict)`
- Metrics: `jobs_total`, `jobs_passed`, `jobs_failed`
### 0.J Spec Lifecycle Governance
- Gate changes are MAJOR.
### 0.K Failure and Error Semantics
- Any required gate failure is deterministic fail.
### 0.L Input/Data Provenance
- All job inputs must be content-addressed.

---
## 2) System Model
### I.A Persistent State
- CI matrix definition and historical gate snapshots.
### I.B Inputs and Hyperparameters
- commit, matrix definition, thresholds, test manifests.
### I.C Constraints and Feasible Set
- Valid iff all required jobs complete and required gates pass.
### I.D Transient Variables
- job outputs, logs, normalized verdicts.
### I.E Invariants and Assertions
- No skipped required jobs.

---
## 3) Initialization
1. Load matrix definition.
2. Validate worker environment.
3. Resolve required job graph.

---
## 4) Operator Manifest
- `Glyphser.CI.RunBuild`
- `Glyphser.CI.RunTestSuite`
- `Glyphser.CI.EvaluateGates`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.CI.RunBuild`  
**Signature:** `(build_target, env -> build_result)`  
**Purity class:** IO  
**Determinism:** deterministic with pinned toolchain.

**Operator:** `Glyphser.CI.RunTestSuite`  
**Signature:** `(suite_id, artifact -> test_result)`  
**Purity class:** IO  
**Determinism:** deterministic with fixed seeds and fixtures.

**Operator:** `Glyphser.CI.EvaluateGates`  
**Signature:** `(job_results, gate_policy -> gate_verdict)`  
**Purity class:** PURE  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. RunBuild for required targets
2. RunTestSuite per matrix job
3. EvaluateGates
4. Emit ci_report
```

---
## 7) Trace & Metrics
### Logging rule
- CI emits deterministic job and gate records.
### Trace schema
- `run_header`: matrix_hash, commit_hash
- `iter`: job_id, status, artifact_hash
- `run_end`: gate_verdict, report_hash
### Metric schema
- `jobs_total`, `jobs_passed`, `jobs_failed`
### Comparability guarantee
- Comparable iff matrix, policy, and inputs are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Required jobs declared and reachable.
#### VII.B Operator test vectors (mandatory)
- Matrix reduction and gate boundary tests.
#### VII.C Golden traces (mandatory)
- Golden CI matrix traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for gate verdict and report hash.
#### VIII.B Allowed refactor categories
- CI backend changes preserving normalized outputs.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of verdicts on frozen job outputs.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- Job cursor and partial result map.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed CI run must produce same final verdict.

---
## 11) Related Contracts
- `docs/layer4-implementation/EQC-CI-Policy.md`
- `docs/layer4-implementation/Spec-Lint-Rules.md`
