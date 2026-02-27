# Glyphser Distributed Failure Recovery Guide
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Runtime.DistributedFailureRecovery`  
**Purpose (1 sentence):** Define deterministic distributed failure detection, lease handling, restart sequencing, and recovery validation.  
**Spec Version:** `Glyphser.Runtime.DistributedFailureRecovery` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Distributed runtime reliability.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Runtime.DistributedFailureRecovery`
- **Purpose (1 sentence):** Deterministic distributed failure recovery contract.
### 0.A Objective Semantics
- minimize unrecoverable distributed run states and split-brain risk.
### 0.B Reproducibility Contract
- recovery outcomes reproducible from `(failure_event_log_hash, lease_policy_hash, checkpoint_hash)`.
### 0.C Numeric Policy
- lease counters and epochs are uint64 exact.
### 0.D Ordering and Tie-Break Policy
- recovery actions ordered by `(epoch, rank, event_seq)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- rank-level checks parallelized; recovery plan aggregation deterministic.
### 0.F Environment and Dependency Policy
- distributed backend profile and timeout policy pinned.
### 0.G Operator Manifest
- `Glyphser.Runtime.DetectFailureEvent`
- `Glyphser.Runtime.ResolveLeaseState`
- `Glyphser.Runtime.ComputeRecoveryPlan`
- `Glyphser.Runtime.ExecuteRecoveryPlan`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Runtime.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(recovery_report, restart_plan_hash, final_cluster_state)`.
### 0.J Spec Lifecycle Governance
- lease/restart policy changes are MAJOR.
### 0.K Failure and Error Semantics
- unresolved lease conflicts fail closed deterministically.
### 0.L Input/Data Provenance
- all failure events and lease transitions are trace-bound.

---
## 2) System Model
### I.A Persistent State
- lease table, rank health state, recovery epoch.
### I.B Inputs and Hyperparameters
- failure events, lease TTL policy, checkpoint refs.
### I.C Constraints and Feasible Set
- exactly one active lease owner per partition.
### I.D Transient Variables
- per-rank health checks and plan candidates.
### I.E Invariants and Assertions
- no split-brain committed state transitions.

---
## 3) Initialization
1. Load cluster lease and health snapshots.
2. Validate last committed checkpoint binding.
3. Initialize recovery epoch context.

---
## 4) Operator Manifest
- `Glyphser.Runtime.DetectFailureEvent`
- `Glyphser.Runtime.ResolveLeaseState`
- `Glyphser.Runtime.ComputeRecoveryPlan`
- `Glyphser.Runtime.ExecuteRecoveryPlan`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Runtime.DetectFailureEvent`
**Signature:** `(cluster_state, health_signals -> failure_events)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Canonically classifies rank/node failures and emits ordered failure events.

**Operator:** `Glyphser.Runtime.ResolveLeaseState`
**Signature:** `(lease_table, failure_events, lease_policy -> lease_state)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Resolves lease ownership with deterministic epoch/rank tie-breaking and split-brain prevention.

**Operator:** `Glyphser.Runtime.ComputeRecoveryPlan`  
**Signature:** `(cluster_state, failure_events, lease_state -> recovery_plan)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Produces deterministic restart/eviction/rejoin plan.

**Operator:** `Glyphser.Runtime.ExecuteRecoveryPlan`
**Signature:** `(recovery_plan, cluster_state -> recovery_report, final_cluster_state)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Executes ordered recovery actions and validates resulting cluster state.

---
## 6) Procedure
```text
1. failure_events <- DetectFailureEvent
2. lease_state <- ResolveLeaseState
3. recovery_plan <- ComputeRecoveryPlan
4. recovery_report, final_cluster_state <- ExecuteRecoveryPlan
5. restart_plan_hash <- SHA-256(CBOR_CANONICAL(recovery_plan))
6. return (recovery_report, restart_plan_hash, final_cluster_state)
```

---
## 7) Trace & Metrics
- Metrics: `failed_ranks`, `recovery_attempts`, `recovery_success`, `split_brain_prevented`.
- Trace includes epoch, lease transitions, restart actions.

---
## 8) Validation
- rank loss and network partition scenario tests.
- deterministic restart ordering and lease conflict tests.

---
## 9) Refactor & Equivalence
- E0 for recovery plan hash and final cluster-state verdict.

---
## 10) Checkpoint/Restore
- checkpoint stores recovery epoch, lease table, pending plan hash.
- restore resumes recovery workflow deterministically.

---
## 11) Distributed Failure Fingerprint Standard (Normative)
- Every distributed recovery incident MUST emit a compact deterministic failure fingerprint:
  - `failure_operator`,
  - `failure_code`,
  - `first_divergence_step`,
  - `rank_set_hash`,
  - `network_state_hash`,
  - `recovery_plan_hash`,
  - `trace_segment_hash`.
- Fingerprint identity:
  - `distributed_failure_fingerprint_hash = SHA-256(CBOR_CANONICAL(failure_fingerprint))`.
- Support workflow requirement:
  - fingerprint is the primary cross-environment triage key.
