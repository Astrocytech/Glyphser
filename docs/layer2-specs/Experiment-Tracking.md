# Glyphser Experiment Tracking Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Tracking.ExperimentTracking`  
**Purpose (1 sentence):** Define deterministic run/metric/artifact tracking APIs and storage contracts for lifecycle observability.  
**Spec Version:** `Glyphser.Tracking.ExperimentTracking` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Experiment tracking and artifact lifecycle.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Tracking.ExperimentTracking`
- **Purpose (1 sentence):** Deterministic experiment/run tracking.
- **Spec Version:** `Glyphser.Tracking.ExperimentTracking` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Tracking and artifacts.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize tracking ambiguity and non-replayable run metadata.
### 0.B Reproducibility Contract
- Replayable given `(run_id, tracking_store_hash, artifact_index_hash)`.
### 0.C Numeric Policy
- Metric values in binary64; identifiers exact.
### 0.D Ordering and Tie-Break Policy
- Events ordered by `(t, operator_seq, rank)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Concurrent metric writes merged deterministically.
### 0.F Environment and Dependency Policy
- Tracking backend must expose content-addressable artifact APIs.
### 0.G Operator Manifest
- `Glyphser.Tracking.RunCreate`
- `Glyphser.Tracking.RunStart`
- `Glyphser.Tracking.RunEnd`
- `Glyphser.Tracking.MetricLog`
- `Glyphser.Tracking.ArtifactPut`
- `Glyphser.Tracking.ArtifactGet`
- `Glyphser.Tracking.ArtifactList`
- `Glyphser.Tracking.ArtifactTombstone`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Tracking.*` operators.
### 0.I Outputs and Metric Schema
- Outputs: `(tracking_report, artifact_index_hash)`
- Metrics: `run_count`, `metric_events`, `artifact_count`
- Completion status: `success | failed`
### 0.J Spec Lifecycle Governance
- API/signature changes require MAJOR.
### 0.K Failure and Error Semantics
- Deterministic failures on invalid run/artifact operations.
### 0.L Input/Data Provenance
- Every artifact must include content hash and tenant scope.

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
- run registry and artifact index.
### I.B Inputs and Hyperparameters
- `tenant_id`, `run_id`, metric payloads, artifact metadata.
### I.C Constraints and Feasible Set
- run_id unique per tenant/project.
### I.D Transient Variables
- write buffers and upload diagnostics.
### I.E Invariants and Assertions
- immutable run lineage; append-only metrics/events.

### II.F CAS Retention and GC Policy (Normative)
- Artifacts and event objects are content-addressed and immutable.
- Retention classes: `golden`, `certified_release`, `experimental`, `ephemeral`.
- Physical deletion is prohibited while object is reachable from active execution certificates or pinned model releases.
- GC must be deterministic mark/sweep over declared roots and emit hash-chained GC audit records.

### II.G Canonical Tracking Record Schemas (Normative)
- `RunRecord` (CBOR map):
  - `tenant_id:string`, `run_id:string`, `replay_token:bytes32`, `manifest_hash:bytes32`, `trace_final_hash:bytes32`, `checkpoint_hash:bytes32`, `execution_certificate_hash:bytes32`, `status:string`, `created_at:string`, `ended_at?:string`.
- `MetricRecord` (CBOR map):
  - `tenant_id:string`, `run_id:string`, `metric_name:string`, `metric_value:float64`, `metric_step:uint64`, `aggregation:enum(raw|sum|mean|min|max|quantile)`, `quantile_p?:float64`, `window_id?:string`, `recorded_at:string`.
  - semantics: each metric record stores one scalar observation; `aggregation` denotes producer-side semantic label and does not trigger query-time aggregation by itself.
- `ArtifactRecord` (CBOR map):
  - `tenant_id:string`, `run_id:string`, `artifact_id:string`, `artifact_digest:bytes32`, `artifact_size_bytes:uint64`, `storage_locator:string`, `artifact_class:string`, `created_at:string`, `tombstoned_at?:string`, `tombstone_reason?:string`.
- Type alias note: `digest_ref` (when used externally) resolves to `bytes32` in this contract version.
- Record hash rule:
  - `record_hash = SHA-256(CBOR_CANONICAL(record_map))`.
  - For `MetricRecord`, the canonical `record_map` used for hashing omits `recorded_at`; `recorded_at` remains stored metadata for human/audit readability only.

### II.H Tracking Gate Binding (Normative)
- Any tracking record used by policy gates must be hash-addressed.
- If a gate decision depends on tracking evidence, the decision transcript must include the relevant `record_hash` values and bind them through `policy_gate_hash`.
- For regulated/confidential modes, retention rules must preserve all gate-referenced records until retention expiry.

### II.I Artifact and Index Commitments (Normative)
- `artifact_id = SHA-256(artifact_bytes)` for raw artifacts; when metadata must be committed, use `SHA-256(CBOR_CANONICAL(["artifact", [artifact_bytes_hash, metadata_hash]]))`.
- `artifact_index_hash` is computed as:
  - `metadata_hash_i = SHA-256(CBOR_CANONICAL(artifact_metadata_i))`, where `artifact_metadata_i` is the canonical metadata map stored for artifact `i`.
  - `artifact_leaf_i = SHA-256(CBOR_CANONICAL(["artifact_index_leaf", [artifact_id_i, metadata_hash_i, status_i]]))`,
  - sorted by `artifact_id`,
  - Merkle odd-leaf rule duplicates the last leaf.
- Idempotency rule: repeated `ArtifactPut` with identical `(run_id, artifact_id)` must return the existing record deterministically.
- `run_record_hash = SHA-256(CBOR_CANONICAL(RunRecord))`.
  - mutability note: `RunRecord` is mutable until `RunEnd` finalizes terminal fields; `run_record_hash` is final only after run end, and pre-final uses are undefined.
- `tracking_store_hash` definition (normative):
  - `tracking_store_hash = SHA-256(CBOR_CANONICAL(["tracking_store", [run_record_hash, metric_stream_hash, artifact_index_hash]]))`,
  - `metric_stream_hash` is computed as a deterministic hash-chain over `MetricRecord` hashes sorted by `(metric_step, metric_name, record_hash)`:
    - `h_0 = SHA-256(CBOR_CANONICAL(["metric_chain", []]))`,
    - for each sorted record hash `record_hash_i`: `h_i = SHA-256(CBOR_CANONICAL(["metric_chain", [h_{i-1}, record_hash_i]]))`,
    - final `metric_stream_hash = h_n`.
  - `recorded_at` is informational metadata only and MUST NOT affect deterministic ordering/hash commitments.

---
## 3) Initialization
1. Initialize tracking store bindings.
2. Validate tenant/project namespace.
3. Initialize run/event streams.

---
## 4) Operator Manifest
- `Glyphser.Tracking.RunCreate`
- `Glyphser.Tracking.RunStart`
- `Glyphser.Tracking.RunEnd`
- `Glyphser.Tracking.MetricLog`
- `Glyphser.Tracking.ArtifactPut`
- `Glyphser.Tracking.ArtifactGet`
- `Glyphser.Tracking.ArtifactList`
- `Glyphser.Tracking.ArtifactTombstone`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
External operator reference: `Glyphser.Error.Emit` is defined in `docs/layer1-foundation/Error-Codes.md`.

**Operator:** `Glyphser.Tracking.RunCreate`  
**Category:** IO  
**Signature:** `(tenant_id, run_manifest -> run_id)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** creates immutable run metadata anchor with placeholder terminal fields (`trace_final_hash`, `ended_at`) unset.

**Operator:** `Glyphser.Tracking.RunStart`  
**Category:** IO  
**Signature:** `(run_id, start_metadata -> ok)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** appends deterministic run-start event and transitions run lifecycle to ACTIVE.

**Operator:** `Glyphser.Tracking.RunEnd`  
**Category:** IO  
**Signature:** `(run_id, end_metadata -> ok)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** appends deterministic run-end event, atomically sets terminal run fields (`trace_final_hash`, `ended_at`, status), and seals the run event stream.

**Operator:** `Glyphser.Tracking.MetricLog`  
**Category:** IO  
**Signature:** `(run_id, metric_event -> ok)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** appends typed metric event.

**Operator:** `Glyphser.Tracking.ArtifactPut`  
**Category:** IO  
**Signature:** `(run_id, artifact_bytes, metadata -> artifact_id)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** stores content-addressed artifact and updates index.

**Operator:** `Glyphser.Tracking.ArtifactGet`  
**Category:** IO  
**Signature:** `(run_id, artifact_id -> artifact_bytes, metadata)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** resolves artifact by content-addressed identifier and returns immutable bytes + metadata.

**Operator:** `Glyphser.Tracking.ArtifactList`  
**Category:** IO  
**Signature:** `(run_id, filter? -> artifact_index)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** lists artifacts in canonical order (artifact_id ascending) with deterministic filtering.

**Operator:** `Glyphser.Tracking.ArtifactTombstone`
**Category:** IO
**Signature:** `(run_id, artifact_id, reason -> tombstone_id)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** appends immutable tombstone metadata; physical deletion is deferred to retention policy. Tombstoned artifacts remain retrievable by `artifact_id` for audit/replay, and are marked as deleted in listing views.
`reason` is required and MUST be a valid UTF-8 string; it MUST be persisted into `tombstone_reason` and therefore committed by `record_hash`.

---
## 6) Procedure
```text
1. RunCreate
2. RunStart
3. MetricLog / ArtifactPut repeated
4. ArtifactTombstone optional
5. RunEnd
6. Return tracking_report
```

---
## 7) Trace & Metrics
### Logging rule
- Tracking operations emit deterministic run/metric/artifact events.
### Trace schema
- `run_header`: tenant_id, run_id
- `iter`: event_type, key, status
- `run_end`: artifact_index_hash
### Metric schema
- `metric_events`, `artifact_count`
### Comparability guarantee
- Comparable iff schemas, run IDs, and content hashes are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- signature-locked APIs, typed events, hash-addressed artifacts.
#### VII.B Operator test vectors (mandatory)
- create/start/end flow, invalid state transitions, artifact hash mismatch.
#### VII.C Golden traces (mandatory)
- golden run-tracking traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for run/artifact identifiers and trace outputs.
#### VIII.B Allowed refactor categories
- storage backend optimization preserving IDs and hashes.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of run metadata + artifact index hash.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- run cursor and artifact index watermark.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed tracking yields identical IDs/order under same inputs.
