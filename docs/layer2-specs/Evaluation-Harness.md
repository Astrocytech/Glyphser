# Glyphser Evaluation Harness Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Eval.Harness`  
**Purpose (1 sentence):** Define deterministic safety/bias/robustness evaluation runs and evidence bundles linked to registry/deployment policy gates.  
**Spec Version:** `Glyphser.Eval.Harness` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Evaluation governance and evidence generation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Eval.Harness`
- **Purpose (1 sentence):** Replayable evaluation evidence contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize unsafe/unvetted deployments.
### 0.B Reproducibility Contract
- Replayable given `(eval_manifest_hash, dataset_snapshot_id, determinism_tier)`.
### 0.C Numeric Policy
- Metrics in binary64 with explicit thresholds.
### 0.D Ordering and Tie-Break Policy
- Test case ordering deterministic by case_id.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-rank evaluation aggregation deterministic.
### 0.F Environment and Dependency Policy
- Evaluation must declare determinism tier (`E0` or `E1`) and tolerance map.
### 0.G Operator Manifest
- `Glyphser.Eval.RunSuite`
- `Glyphser.Eval.AggregateMetrics`
- `Glyphser.Eval.BuildEvidenceBundle`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Eval.*`
### 0.I Outputs and Metric Schema
- Outputs: `(eval_report, evidence_bundle_ref)`
- Metrics: `safety_score`, `bias_score`, `robustness_score`
### 0.J Spec Lifecycle Governance
- evaluation metric semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- abort on schema mismatch or missing evidence references.
### 0.L Input/Data Provenance
- evaluation must bind `dataset_snapshot_id` and model version hash.

---
### 0.Z EQC Mandatory Declarations Addendum
- Seed space: `seed ∈ {0..2^64-1}` when stochastic sub-operators are used.
- PRNG family: `Philox4x32-10` for declared stochastic operators.
- Randomness locality: all sampling occurs only inside declared stochastic operators in section 5.
- Replay guarantee: replayable given (seed, PRNG family, numeric policy, ordering policy, parallel policy, environment policy).
- Replay token: deterministic per-run token contribution is defined and included in trace records.
- Floating-point format: IEEE-754 binary64 unless explicitly declared otherwise.
- Rounding mode: round-to-nearest ties-to-even unless explicitly overridden.
- Fast-math policy: forbidden for critical checks and verdict paths.
- Named tolerances: `EPS_EQ=1e-10`, `EPS_DENOM=1e-12`, and domain-specific thresholds as declared.
- NaN/Inf policy: invalid values trigger deterministic failure handling per 0.K.
- Normalized exponentials: stable log-sum-exp required when exponential paths are used (otherwise N/A).
- Overflow/underflow: explicit abort or clamp behavior must be declared (this contract uses deterministic abort on critical paths).
- Approx-equality: `a ≈ b` iff `|a-b| <= EPS_EQ` when tolerance checks apply.
- Transcendental functions policy: deterministic implementation requirements are inherited from consuming operators.
- Reference runtime class: CPU-only/GPU-enabled/distributed as required by the consuming workflow.
- Compiler/flags: deterministic compilation; fast-math disabled for critical paths.
- Dependency manifest: pinned runtime dependencies and versions are required.
- Determinism level: `BITWISE` for contract-critical outputs unless a stricter local declaration exists.
- Error trace rule: final failure record includes `t`, `failure_code`, `failure_operator`, replay token, and minimal diagnostics.
- Recovery policy: none unless explicitly declared; default is deterministic abort-only.

## 2) System Model
### I.A Persistent State
- eval suite definitions and threshold policies.
### I.B Inputs and Hyperparameters
- eval manifest, dataset snapshot, model artifact ref.
### I.C Constraints and Feasible Set
- evidence bundle required for policy-gated promotion.
### I.D Transient Variables
- per-case metrics and aggregated scores.
### I.E Invariants and Assertions
- evidence includes trace root and metrics digest.

### II.F Evidence Bundle (Normative)
- `eval_manifest_hash`
- `dataset_snapshot_id`
- `metrics_digest`
  - `metrics_digest = SHA-256(CBOR_CANONICAL(sorted_metrics))` where `sorted_metrics` is canonical array of `{name, value, unit?}` sorted by `name`.
- `trace_final_hash`
- `determinism_tier`
  - allowed values: `E0 | E1` as defined in `docs/layer2-specs/Replay-Determinism.md`.
  - enforcement rule: `E0` requires bitwise equality for designated critical outputs; `E1` uses tolerance-based comparators from the active determinism profile/eval config.
  - critical-output source of truth: designated critical outputs are those marked `E0` by the active determinism profile/class map for the evaluation suite.
- `replay_token`
- `aggregation_policy` schema (normative):
  - map `metric_name -> {agg: enum("mean","sum","min","max","quantile"), quantile_p?:float64}`.
  - quantile rule (normative): when `agg="quantile"`, compute nearest-rank quantile on ascending sorted values with index `k = floor(p * (n-1))` (0-based), value=`sorted[k]`.
- `evidence_bundle_ref` points to canonical CBOR payload:
  - `{eval_manifest_hash, dataset_snapshot_id, metrics_digest, trace_final_hash, determinism_tier, replay_token, eval_report_hash}`.
  - `eval_report_hash = SHA-256(CBOR_CANONICAL(eval_report))`, where `eval_report` is the output of `AggregateMetrics`.

---
## 3) Initialization
1. Validate eval manifest and dataset snapshot.
2. Load model artifact and determinism profile.
3. Initialize evaluation run context.

---
## 4) Operator Manifest
- `Glyphser.Eval.RunSuite`
- `Glyphser.Eval.AggregateMetrics`
- `Glyphser.Eval.BuildEvidenceBundle`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Eval.RunSuite`  
**Category:** Governance  
**Signature:** `(eval_manifest, model_ref, dataset_snapshot_ref -> suite_run_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** executes the declared evaluation suite in deterministic case order and emits per-case results.

**Operator:** `Glyphser.Eval.AggregateMetrics`  
**Category:** Governance  
**Signature:** `(suite_run_report, aggregation_policy -> eval_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** aggregates per-case metrics into canonical summary outputs and threshold verdicts.

**Operator:** `Glyphser.Eval.BuildEvidenceBundle`  
**Category:** Governance  
**Signature:** `(eval_report, trace_ref, dataset_snapshot_ref -> evidence_bundle_ref)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** builds content-addressed evidence bundle for downstream policy gates, with `trace_final_hash` computed from the actual evaluation trace referenced by `trace_ref`.

---
## 6) Procedure
```text
1. RunSuite
2. AggregateMetrics
3. BuildEvidenceBundle
4. Return eval_report + evidence_bundle_ref
```

---
## 7) Trace & Metrics
### Logging rule
- evaluation events emit deterministic suite/case metrics.
### Trace schema
- `run_header`: eval_manifest_hash, dataset_snapshot_id
- `iter`: case_id, metrics, status
- `run_end`: metrics_digest, evidence_bundle_ref
### Metric schema
- safety/bias/robustness metrics + threshold verdicts.
### Comparability guarantee
- comparable iff same manifest, snapshot, determinism tier, and thresholds.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- evidence completeness and replay linkage.
#### VII.B Operator test vectors (mandatory)
- deterministic evaluation on fixed datasets and tolerance-tier tests.
#### VII.C Golden traces (mandatory)
- golden evidence bundle digests.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for evidence bundle and pass/fail verdict on frozen inputs.
#### VIII.B Allowed refactor categories
- suite execution optimization preserving metrics/verdicts.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of metrics digest + verdict.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- evaluation cursor and partial metrics state.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed evaluation yields identical evidence bundle for same inputs.
