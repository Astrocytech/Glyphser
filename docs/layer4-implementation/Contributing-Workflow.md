# Glyphser Contributing Workflow Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.ContributingWorkflow`  
**Purpose (1 sentence):** Define deterministic contribution lifecycle from branch creation to merge with mandatory evidence gates.  
**Spec Version:** `Glyphser.Implementation.ContributingWorkflow` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Engineering collaboration and merge governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.ContributingWorkflow`
- **Purpose (1 sentence):** Deterministic contribution workflow contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: prevent unverified changes from entering mainline.
### 0.B Reproducibility Contract
- Replayable given `(pr_id, commit_set_hash, ci_report_hash, review_decision_hash)`.
### 0.C Numeric Policy
- Gate thresholds and counts use exact deterministic comparisons.
### 0.D Ordering and Tie-Break Policy
- Workflow transitions are strictly ordered and append-only.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multiple reviewers allowed; merge verdict uses deterministic reduction policy.
### 0.F Environment and Dependency Policy
- Contributor environments must pass `Developer-Setup.md` checks.
### 0.G Operator Manifest
- `Glyphser.Contrib.OpenPR`
- `Glyphser.Contrib.RunRequiredChecks`
- `Glyphser.Contrib.RecordReview`
- `Glyphser.Contrib.MergePR`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Contrib.*`
### 0.I Outputs and Metric Schema
- Outputs: `(workflow_report, merge_verdict)`
- Metrics: `checks_passed`, `reviews_approved`
### 0.J Spec Lifecycle Governance
- Required check/review policy changes are MAJOR.
### 0.K Failure and Error Semantics
- Missing required checks or approvals blocks merge.
### 0.L Input/Data Provenance
- Decisions must reference immutable check/review artifacts.

---
## 2) System Model
### I.A Persistent State
- PR state machine and review ledger.
### I.B Inputs and Hyperparameters
- PR metadata, required checks, review policy.
### I.C Constraints and Feasible Set
- Merge valid iff all required conditions are met.
### I.D Transient Variables
- Check outputs and review diagnostics.
### I.E Invariants and Assertions
- No direct merge bypass for protected branches.

---
## 3) Initialization
1. Validate PR metadata.
2. Resolve required checks/reviews.
3. Initialize transition ledger.

---
## 4) Operator Manifest
- `Glyphser.Contrib.OpenPR`
- `Glyphser.Contrib.RunRequiredChecks`
- `Glyphser.Contrib.RecordReview`
- `Glyphser.Contrib.MergePR`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Contrib.OpenPR`
**Signature:** `(pr_metadata -> pr_id)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Creates canonical PR record and returns immutable `pr_id`.

**Operator:** `Glyphser.Contrib.RunRequiredChecks`  
**Signature:** `(pr_id, check_policy -> check_report)`  
**Purity class:** IO  
**Determinism:** deterministic.

**Operator:** `Glyphser.Contrib.RecordReview`  
**Signature:** `(pr_id, reviewer_id, verdict, notes_hash -> review_record)`  
**Purity class:** IO  
**Determinism:** deterministic.

**Operator:** `Glyphser.Contrib.MergePR`  
**Signature:** `(pr_id, check_report, review_records -> merge_verdict)`  
**Purity class:** IO  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. OpenPR
2. RunRequiredChecks
3. RecordReview (one or more)
4. MergePR
5. return (workflow_report, merge_verdict)
```

---
## 7) Trace & Metrics
### Logging rule
- Workflow steps emit deterministic PR transition events.
### Trace schema
- `run_header`: pr_id, base_branch
- `iter`: transition_id, status
- `run_end`: merge_verdict
### Metric schema
- `checks_passed`, `reviews_approved`
### Comparability guarantee
- Comparable iff same PR commit set and policy.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Required transitions/checks/reviews enforced.
#### VII.B Operator test vectors (mandatory)
- Pass/fail workflow scenarios.
#### VII.C Golden traces (mandatory)
- Golden PR lifecycle traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for merge verdict and transition log.
#### VIII.B Allowed refactor categories
- Tooling integration changes preserving decisions.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of workflow outcomes.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- PR workflow cursor and pending actions.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed workflow must preserve final merge verdict.
