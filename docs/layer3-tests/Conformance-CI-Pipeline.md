# Glyphser Conformance CI Pipeline Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.ConformanceCIPipeline`  
**Purpose (1 sentence):** Define deterministic CI pipeline stages for contract linting, conformance suites, replay checks, and release gating.  
**Spec Version:** `Glyphser.Implementation.ConformanceCIPipeline` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** CI/CD conformance governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.ConformanceCIPipeline`
- **Purpose (1 sentence):** Deterministic CI gate graph contract.
### 0.A Objective Semantics
- minimize false passes and nondeterministic gate outcomes.
### 0.B Reproducibility Contract
- pipeline verdict reproducible from `(commit_hash, lockfile_hash, ci_policy_hash)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- binary64 for aggregate timing and score metrics.
### 0.D Ordering and Tie-Break Policy
- stage order fixed: lint -> unit -> integration -> replay -> evidence -> gates.
### 0.E Parallel, Concurrency, and Reduction Policy
- intra-stage parallel allowed; stage barriers strict.
### 0.F Environment and Dependency Policy
- CI runtime pinned with runtime_env_hash.
### 0.G Operator Manifest
- `Glyphser.CI.RunStage`
- `Glyphser.CI.AggregateStageResults`
- `Glyphser.CI.EmitGateVerdict`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.CI.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(ci_report, gate_verdict, artifact_bundle_hash)`.
### 0.J Spec Lifecycle Governance
- mandatory stage set changes are MAJOR.
### 0.K Failure and Error Semantics
- required stage failure aborts pipeline.
### 0.L Input/Data Provenance
- CI artifacts are content-addressed and hash-bound.
### 0.Z EQC Mandatory Declarations Addendum
- seed space: N/A (pipeline control flow is deterministic and non-stochastic).
- PRNG family: N/A.
- replay guarantee: identical `(commit_hash, lockfile_hash, ci_policy_hash)` yields identical `gate_verdict`.
- floating-point format: IEEE-754 binary64 for informational timing metrics.
- NaN/Inf policy: invalid in gate-affecting metrics.
- default tolerances: `abs_tol=EPS_EQ`, `rel_tol=0` unless stage policy overrides.
- determinism target: E0 for stage pass/fail sequence and gate verdict.

---
## 2) System Model
### I.A Persistent State
- CI policy and stage graph definitions.
### I.B Inputs and Hyperparameters
- commit refs, `lockfile_hash`, target profile, stage toggles.
### I.C Constraints and Feasible Set
- required stages cannot be skipped.
### I.D Transient Variables
- per-stage reports.
### I.E Invariants and Assertions
- gate verdict derived only from frozen stage outputs.

---
## 3) Initialization
1. Load CI pipeline policy.
2. Resolve mandatory stage list.
3. Initialize stage runner context.

---
## 4) Operator Manifest
- `Glyphser.CI.RunStage`
- `Glyphser.CI.AggregateStageResults`
- `Glyphser.CI.EmitGateVerdict`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.CI.RunStage`  
**Signature:** `(stage_id, inputs -> stage_report)`  
**Purity class:** IO  
**Determinism:** deterministic inputs/result schema  
**Definition:** Executes CI stage and emits canonical report object.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `CI_STAGE_FAILURE`, `ARTIFACT_MISSING`.

**Operator:** `Glyphser.CI.AggregateStageResults`
**Signature:** `(stage_reports, ci_policy -> gate_report, artifact_bundle_hash)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Aggregates stage reports in fixed stage order and computes `artifact_bundle_hash` over canonical artifact manifest.
**allowed_error_codes:** `CONTRACT_VIOLATION`.

**Operator:** `Glyphser.CI.EmitGateVerdict`
**Signature:** `(gate_report, artifact_bundle_hash -> gate_verdict, ci_report)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Emits canonical gate verdict and finalized CI report.
**allowed_error_codes:** `CONTRACT_VIOLATION`.

---
## 6) Procedure
```text
1. Run required stages in fixed order
2. Collect stage reports
3. Aggregate deterministic gate report and compute `artifact_bundle_hash`
4. Emit deterministic gate verdict and publish report
```

---
## 7) Trace & Metrics
- Metrics: `stages_total`, `stages_passed`, `stages_failed`, `pipeline_duration_s` (informational only; excluded from deterministic gate decision).
- Trace includes stage ids, stage hashes, and final gate decision.

---
## 8) Validation
- golden CI graphs for pass/fail scenarios.
- failure-injection tests for stage interruption/recovery.

---
## 9) Refactor & Equivalence
- E0 for gate verdict and stage result hashes.

---
## 10) Checkpoint/Restore
- checkpoint stores `completed_stage_ids[]`, `stage_cursor`, `partial_stage_reports_hash`, and `artifact_bundle_hash` (if already materialized).
- restore resumes from next unfinished stage deterministically.
