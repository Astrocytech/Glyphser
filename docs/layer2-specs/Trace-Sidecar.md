# Glyphser Trace Sidecar Schema
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Trace.SidecarSchema`  
**Purpose (1 sentence):** Define a canonical machine-readable trace schema shared by all Glyphser components.  
**Spec Version:** `Glyphser.Trace.SidecarSchema` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Trace interoperability and comparability.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Trace.SidecarSchema`
- **Purpose (1 sentence):** Canonical trace schema contract.
- **Spec Version:** `Glyphser.Trace.SidecarSchema` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Unified trace format.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize trace ambiguity and schema drift.
### 0.B Reproducibility Contract
- Replayable given `(schema_version, trace_final_hash, replay_token_formula)`.
### 0.C Numeric Policy
- Field types are explicit; numeric fields use declared scalar kinds.
### 0.D Ordering and Tie-Break Policy
- Canonical record order:
  - `RUN_HEADER` is always first,
  - `ITER` records are sorted by `(t, rank, operator_seq)`,
  - `RUN_END` is always last.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-rank traces merged in one canonical total order: `(t, rank, operator_seq)`.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for schema and required key set.
### 0.G Operator Manifest
- `Glyphser.Trace.ValidateSchema`
- `Glyphser.Trace.NormalizeRecord`
- `Glyphser.Trace.ComputeTraceHash`
### 0.H Namespacing and Packaging
- Namespaced schema keys required.
### 0.I Outputs and Metric Schema
- Outputs: `(normalized_trace, trace_final_hash)`.
- Metrics: `record_count`, `missing_required_keys`.
- Completion status: `success | failed`.
### 0.J Spec Lifecycle Governance
- Required-key changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on schema violations in strict mode.
### 0.L Input/Data Provenance
- Trace source component and replay context required.

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
- trace schema registry.
### I.B Inputs and Hyperparameters
- raw trace stream and schema version.
### I.C Constraints and Feasible Set
- valid iff required keys/types are present.
### I.D Transient Variables
- normalized records and diagnostics.
### I.E Invariants and Assertions
- key set and type contract invariant.

### II.F Canonical Trace Schema (Concrete)
- Hash algorithms:
  - `record_hash_i = SHA-256(CBOR_CANONICAL(normalized_record_i))`
  - Whole-run hash chain:
    - `h_0 = SHA-256(CBOR_CANONICAL(["trace_chain", []]))`
    - `h_i = SHA-256(CBOR_CANONICAL(["trace_chain", [h_{i-1}, record_hash_i]]))` for records in canonical order
    - `trace_final_hash = h_last`
- Trace endpoints:
  - `trace_head_hash = h_0`
  - `trace_final_hash = h_last`
- Self-reference rule: when hashing the `run_end` record, `run_end.trace_final_hash` is omitted from the canonical CBOR map input.
- Empty-bytes substitution is forbidden for omitted fields in canonical hashing paths.
- Canonical serialization: `CBOR_CANONICAL` from `docs/layer1-foundation/Canonical-CBOR-Profile.md`.
- `TraceRecord` union (normative):
  - `kind: enum("RUN_HEADER","ITER","POLICY_GATE_VERDICT","CHECKPOINT_COMMIT","CERTIFICATE_INPUTS","RUN_END","ERROR")`.
- Required `RUN_HEADER` fields/types: `kind:"RUN_HEADER"`, `schema_version:string`, `replay_token:bytes32`, `run_id:string`, `tenant_id:string`, `task_type:string`, `world_size:uint32`, `backend_binary_hash:bytes32`, `driver_runtime_fingerprint_hash:bytes32`, `policy_bundle_hash:bytes32`, `monitor_policy_hash:bytes32`, `operator_contracts_root_hash:bytes32`, `redaction_mode:string`, `redaction_key_id?:string`, `redaction_policy_hash?:bytes32`, `hash_gate_M:uint64`, `hash_gate_K:uint64`.
- Optional `run_header` fields/types: `authz_decision_hash?:bytes32`.
- Required `ITER` fields/types: `t:uint64`, `stage_id:string`, `operator_id:string`, `operator_seq:uint64`, `rank:uint32`, `status:string`, `replay_token:bytes32`.
- `operator_seq` is a per-step, per-rank monotone counter:
  - initialize `operator_seq=0` at the start of each `(t, rank)` step scope,
  - increment by 1 for each operator invocation in execution order.
- Uniqueness invariant: there must be at most one `ITER` record for each `(t, rank, operator_seq)` tuple.
- Optional `ITER` fields/types: `loss_total:float64`, `grad_norm:float64`, `state_fp:bytes32`, `functional_fp:bytes32`, `rng_offset_before:uint64`, `rng_offset_after:uint64`.
- Optional `ITER` fields/types: `resource_ledger_hash:bytes32`, `quota_decision:string`, `quota_policy_hash:bytes32`.
  - `resource_ledger_hash = SHA-256(CBOR_CANONICAL(resource_ledger_map))` with deterministic key order.
- Optional `ITER` fields/types: `tracking_event_type:string`, `artifact_id:string`, `metric_name:string`, `metric_value:float64`, `window_id:string`.
- Required `POLICY_GATE_VERDICT` fields/types: `t:uint64`, `policy_gate_hash:bytes32`, `transcript_hash:bytes32`.
  - `transcript_hash = SHA-256(CBOR_CANONICAL(policy_transcript))` where `policy_transcript` is the canonical ordered transcript as defined by the active policy-gate contract (for monitoring gates, see `docs/layer2-specs/Monitoring-Policy.md` II.G).
- Required `CHECKPOINT_COMMIT` fields/types: `t:uint64`, `checkpoint_hash:bytes32`, `checkpoint_header_hash:bytes32`, `checkpoint_merkle_root:bytes32`, `trace_snapshot_hash:bytes32`.
- Required `CERTIFICATE_INPUTS` fields/types: `t:uint64`, `certificate_inputs_hash:bytes32`.
  - `certificate_inputs_hash = SHA-256(CBOR_CANONICAL(certificate_inputs_bundle))` where `certificate_inputs_bundle` is the canonical evidence bundle passed to certificate build/sign flow.
- Required `RUN_END` fields/types: `status:string`, `final_state_fp:bytes32`, `trace_final_hash:bytes32`.
- Required `ERROR` fields/types: `t:uint64`, `failure_code:string`, `failure_operator:string`, `diagnostics_hash:bytes32`.
- Migration controls:
  - `migration_supported_from: array<string>`
  - `migration_operator: string`
  - `migration_invariants: array<string>`

### II.G Privacy Classification and Redaction Contract
- Field classification labels: `PUBLIC | INTERNAL | CONFIDENTIAL`.
- Field-level baseline classes:
  - `PUBLIC`: `t`, `operator_id`, `operator_seq`, hash digests, status.
  - `INTERNAL`: driver/runtime fingerprints, backend/hash metadata.
  - `CONFIDENTIAL`: any value that can leak sample/model-sensitive properties.
- No-raw-data rule: traces must not contain raw examples, prompts, gradients, secrets, or direct identifiers.
- Confidential-mode redaction: sensitive values must be replaced by deterministic keyed hashes (`HMAC-SHA256`) with declared key identifier, as defined in `docs/layer1-foundation/Redaction-Policy.md`.
  - Redacted value encoding (normative): store full HMAC output as `bytes32`.
- Size and sampling controls: deterministic per-operator caps and sampling policy must be declared to bound trace overhead.
- Deterministic size/sampling controls:
  - `max_bytes_per_step:uint64`
  - `max_record_bytes:uint32`
  - `sample_policy: enum("HASH_GATED","FIXED_RATE","OFF")`
  - defaults for `HASH_GATED`: `hash_gate_M=100`, `hash_gate_K=1`.
  - HASH_GATED inclusion rule: include iff `U64_BE(SHA-256(CBOR_CANONICAL([replay_token, [t, operator_seq]]))) mod hash_gate_M < hash_gate_K`.
  - Invariant: `0 <= hash_gate_K <= hash_gate_M` and `hash_gate_M > 0`.
  - Validation requirement: `Glyphser.Trace.ValidateSchema` MUST enforce `hash_gate_M > 0` and `hash_gate_K <= hash_gate_M`; violation is deterministic schema failure.
  - Cap overflow drop policy: `DROP_LOWEST_PRIORITY_CLASS_FIRST` with fixed priority ordering:
    - `RUN_HEADER` > `ERROR` > `POLICY_GATE_VERDICT` > `CHECKPOINT_COMMIT` > `CERTIFICATE_INPUTS` > `RUN_END` > `ITER`.
  - `mandatory_record_kinds = {"RUN_HEADER","POLICY_GATE_VERDICT","CHECKPOINT_COMMIT","CERTIFICATE_INPUTS","RUN_END","ERROR"}`.
  - Mandatory records MUST NEVER be sampled out or dropped.
  - If caps force dropping mandatory records: emit `TRACE_CAP_EXCEEDED_MANDATORY` and abort deterministically.

### II.H Policy Transcript and Run Commit Binding (Normative)
- Policy evaluation must emit a deterministic transcript record stream containing:
  - `policy_input_hashes`, `rule_id`, `rule_version`, `verdict`, `reason_code`.
- Network reads during policy evaluation are forbidden unless inputs are pre-committed and referenced by hash.
- Transcript fold hash:
  - `policy_gate_hash = SHA-256(CBOR_CANONICAL(["policy_transcript", ordered_policy_records]))`.
- `policy_gate_hash` must appear in trace mandatory records and in `Execution-Certificate` signed payload.
- Atomic commit linkage:
  - trace must include `run_commit_prepare` and `run_commit_record` mandatory records,
  - `run_commit_record` must bind `trace_final_hash`, `checkpoint_hash`, `lineage_root_hash`, `certificate_hash`.
- Naming normalization:
  - `trace_final_hash` is the canonical commitment name for this linear hash-chain model (`h_last`).

---
## 3) Initialization
1. Load schema version.
2. Validate required keys.
3. Initialize normalization pipeline.

---
## 4) Operator Manifest
- `Glyphser.Trace.ValidateSchema`
- `Glyphser.Trace.NormalizeRecord`
- `Glyphser.Trace.ComputeTraceHash`

---
## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `Glyphser.Trace.ValidateSchema`  
**Category:** IO  
**Signature:** `(trace, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** required key/type validation.

**Operator:** `Glyphser.Trace.NormalizeRecord`  
**Category:** IO  
**Signature:** `(record -> normalized_record)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical key order and value normalization.

**Operator:** `Glyphser.Trace.ComputeTraceHash`  
**Category:** IO  
**Signature:** `(normalized_trace -> trace_final_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes per-record SHA-256 hashes and folds them with the `trace_chain` hash-chain rule to emit the whole-run `trace_final_hash`.

---
## 6) Procedure
```text
1. ValidateSchema
2. NormalizeRecord for each record
3. ComputeTraceHash
4. Return normalized_trace + hash
```

---
## 7) Trace & Metrics
### Logging rule
Trace schema validation itself emits deterministic validation records.
### Trace schema
- `run_header`: schema_version, source_component
- `iter`: t, operator, validation_status
- `run_end`: trace_final_hash, status
### Metric schema
- `record_count`, `missing_required_keys`
### Comparability guarantee
Comparable iff schema version, key set, and hash formula are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes schema completeness, deterministic ordering, no hidden globals.
#### VII.B Operator test vectors (mandatory)
Valid/invalid trace fixtures.
#### VII.C Golden traces (mandatory)
Golden trace hashes for canonical samples.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for normalized trace and hash.
#### VIII.B Allowed refactor categories
- parser/normalizer optimization preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
Exact normalized record and hash comparison.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- schema version and normalization state.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed validation yields identical outputs.

---
## 11) Observability Bridge Mapping (Normative)
- Glyphser trace/metrics MUST support deterministic export mapping to OpenTelemetry and Prometheus conventions.
- Minimum mapping requirements:
  - `run_header.run_id` -> OTel trace resource attribute `glyphser.run_id`.
  - `iter.operator` -> OTel span attribute `glyphser.operator_id`.
  - `iter.t` -> OTel span attribute `glyphser.step`.
  - `trace_final_hash` -> OTel trace attribute `glyphser.trace_final_hash`.
  - deterministic metric names map to Prometheus-safe snake_case names with fixed units.
- Export mapping identity:
  - `observability_mapping_hash = SHA-256(CBOR_CANONICAL(mapping_table))`.
- Determinism requirement:
  - identical Glyphser trace input MUST produce identical OTel/Prometheus export payloads and identical `observability_mapping_hash`.
- Reference implementation location:
  - `docs/layer4-implementation/Interoperability-Standards-Bridge.md`.
