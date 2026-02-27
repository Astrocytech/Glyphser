# Glyphser Pipeline Orchestrator Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Pipeline.Orchestrator`  
**Purpose (1 sentence):** Define deterministic job lifecycle orchestration and signed transition recording for multi-stage ML pipelines.  
**Spec Version:** `Glyphser.Pipeline.Orchestrator` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Job scheduling and pipeline state governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Pipeline.Orchestrator`
- **Purpose (1 sentence):** Deterministic pipeline/job state orchestration.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize ambiguous job lifecycle transitions.
### 0.B Reproducibility Contract
- Replayable given `(job_manifest_hash, transition_log_hash)`.
### 0.C Numeric Policy
- timestamps and counters deterministic integer types.
### 0.D Ordering and Tie-Break Policy
- transitions ordered by `(job_id, transition_seq)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- queue arbitration deterministic by priority then FIFO.
### 0.F Environment and Dependency Policy
- job manifests must be signed and schema-valid.
### 0.G Operator Manifest
- `Glyphser.Pipeline.JobSubmit`
- `Glyphser.Pipeline.JobTransition`
- `Glyphser.Pipeline.JobHeartbeat`
- `Glyphser.Pipeline.JobCancel`
- `Glyphser.Pipeline.JobQuery`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Pipeline.*` namespace.
### 0.I Outputs and Metric Schema
- Outputs: `(job_state, transition_record)`
- Metrics: `queue_depth`, `job_success_rate`
### 0.J Spec Lifecycle Governance
- state machine changes are MAJOR.
### 0.K Failure and Error Semantics
- invalid transitions abort deterministically.
### 0.L Input/Data Provenance
- all transitions reference signed job manifest hash.

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
- job table and transition log.
### I.B Inputs and Hyperparameters
- job manifest, priority, policy constraints.
- lease policy (`lease_ttl_ticks`, `max_retries`).
- transition controls: `attempt_id`, `transition_seq:uint64`, `backoff_schedule_id`.
  - `attempt_id` is `uint64`, starts at `0` for the initial attempt, and increments by `1` for each retry attempt of the same `job_id`.
- resource quota policy (`gpu_time_budget_ms`, `cpu_time_budget_ms`, `io_bytes_budget`, `memory_bytes_budget`).
### I.C Constraints and Feasible Set
- allowed transitions:
  - `QUEUED -> RUNNING`
  - `QUEUED -> CANCELED`
  - `RUNNING -> SUCCEEDED|FAILED|CANCELED|RETRYING`
  - `RETRYING -> QUEUED|FAILED`
- Multi-scheduler determinism:
  - single authoritative scheduler per queue partition,
  - deterministic partitioning rule: `partition_id = SHA-256(job_id) mod P`,
  - only the partition owner may emit state transitions for that job.
### I.D Transient Variables
- scheduling diagnostics.
- `idempotency_key = SHA-256(CBOR_CANONICAL([tenant_id, [job_id, attempt_id, transition_seq]]))`
### I.E Invariants and Assertions
- no skipped lifecycle states; transition records are append-only.
- running jobs require valid lease and heartbeat.
- quota-denied transitions are deterministic and auditable.

### II.F Resource Ledger and Quota Enforcement (Normative)
- Orchestrator must maintain a deterministic per-job resource ledger:
  - `bytes_allocated`, `peak_bytes`, `io_bytes_read`, `io_bytes_written`, `gpu_time_ms`, `cpu_time_ms`.
- Quota checks must be evaluated before state transition commits and emitted into trace with `quota_policy_hash`.
- Quota violations must map to deterministic error codes and cannot be retried unless policy explicitly allows.

### II.G Supporting Policy Artifacts (Normative)
- `QuotaPolicy` artifact:
  - schema fields: `{quota_policy_hash, gpu_time_budget_ms, cpu_time_budget_ms, io_bytes_budget, memory_bytes_budget, evaluation_rule_id}`.
  - hash: `quota_policy_hash = SHA-256(CBOR_CANONICAL(quota_policy_map))`.
- `BackoffSchedule` artifact:
  - schema fields: `{backoff_schedule_id, delays_ms: array<uint64>, jitter_mode: "NONE"}`.
  - selection rule: retry `k` uses `delays_ms[min(k, len(delays_ms)-1)]`; no random jitter allowed.
- `LeasePolicy` artifact:
  - schema fields: `{lease_policy_id, lease_ttl_ticks:uint64, heartbeat_extension_ticks:uint64, expiry_transition:"RUNNING->RETRYING"}`.
  - lease id: `lease_id = SHA-256(CBOR_CANONICAL([tenant_id, [job_id, attempt_id, transition_seq]]))`.

### II.H Job State Machine (Closed Set, Normative)
- States: `QUEUED`, `RUNNING`, `RETRYING`, `SUCCEEDED`, `FAILED`, `CANCELED`.
- Terminal states: `SUCCEEDED`, `FAILED`, `CANCELED`.
- Allowed transitions:
  - `QUEUED -> RUNNING`
  - `QUEUED -> CANCELED`
  - `RUNNING -> SUCCEEDED | FAILED | CANCELED | RETRYING`
  - `RETRYING -> QUEUED | FAILED` (when retry budget exhausted)
- Any other transition is deterministic `CONTRACT_VIOLATION`.

---
## 3) Initialization
1. Initialize queue and policy checks.
2. Load signing/trust config for manifests.
3. Initialize transition log.

---
## 4) Operator Manifest
- `Glyphser.Pipeline.JobSubmit`
- `Glyphser.Pipeline.JobTransition`
- `Glyphser.Pipeline.JobHeartbeat`
- `Glyphser.Pipeline.JobCancel`
- `Glyphser.Pipeline.JobQuery`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Pipeline.JobSubmit`  
**Category:** Orchestration  
**Signature:** `(job_manifest, priority, idempotency_key -> job_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** validates submission policy and enqueues a new job deterministically.

**Operator:** `Glyphser.Pipeline.JobTransition`  
**Category:** Orchestration  
**Signature:** `(tenant_id, job_id, attempt_id, expected_transition_seq, from_state, to_state, evidence_ref -> transition_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** validates transition against state machine and writes signed transition record atomically; accepted iff stored `transition_seq == expected_transition_seq`, then increments sequence. If `from_state=="RETRYING"` and retry budget is exhausted, only `to_state=="FAILED"` is allowed.
`evidence_ref` format (normative): nullable `bytes32` hash of canonical transition evidence payload (`null` allowed for transitions that require no external evidence).

**Operator:** `Glyphser.Pipeline.JobHeartbeat`
**Category:** Orchestration
**Signature:** `(job_id, lease_id, tick -> heartbeat_record)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** extends lease if `lease_id` matches active running attempt.
`tick` semantics (normative): monotonically increasing `uint64` logical progress counter for the running attempt (for example, step counter or deterministic heartbeat sequence).

**Operator:** `Glyphser.Pipeline.JobCancel`  
**Category:** Orchestration  
**Signature:** `(job_id, principal_id, reason -> cancel_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** requests deterministic cancellation and records authorized terminal/cancel transition.

**Operator:** `Glyphser.Pipeline.JobQuery`  
**Category:** Orchestration  
**Signature:** `(job_id -> job_status_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** returns canonical current state and transition summary for a job.

---
## 6) Procedure
```text
1. JobSubmit
2. JobTransition(QUEUED->RUNNING)
3. JobHeartbeat repeated while RUNNING
4. If lease expires: JobTransition(RUNNING->RETRYING), then RETRYING->QUEUED (bounded retries)
5. JobTransition(RUNNING->terminal)
6. Return final job state
```

Atomicity and deduplication rules:
- Transition write is compare-and-swap on `(job_id, transition_seq)`.
- Duplicate dispatch/ack with same `idempotency_key` must be deduplicated and return the already-committed transition record.
- Conflicting writes must fail deterministically with conflict diagnostics and follow `backoff_schedule_id`.

---
## 7) Trace & Metrics
### Logging rule
- every transition emits a deterministic trace event.
### Trace schema
- `run_header`: orchestrator_version, queue_policy_hash
- `iter`: job_id, from_state, to_state, status
- `run_end`: transition_log_hash, run_commit_record_hash?
### Metric schema
- queue and lifecycle metrics.
### Comparability guarantee
- comparable iff same policy, queue order, and manifest signatures.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- state machine completeness and illegal transition rejection.
#### VII.B Operator test vectors (mandatory)
- legal/illegal transitions, retries, cancellation cases.
#### VII.C Golden traces (mandatory)
- golden job lifecycle traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for transition decisions and transition log.
#### VIII.B Allowed refactor categories
- queue backend changes preserving transition order semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact transition log compare.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- queue state + transition cursor.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed orchestrator yields identical transition sequence.
