# Glyphser Checkpoint Schema Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Checkpoint.SchemaContract`  
**Purpose (1 sentence):** Define deterministic checkpoint structure, compatibility rules, and restore guarantees across Glyphser subsystems.  
**Spec Version:** `Glyphser.Checkpoint.SchemaContract` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** State persistence and restore compatibility.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Checkpoint.SchemaContract`
- **Purpose (1 sentence):** Canonical checkpoint contract.
- **Spec Version:** `Glyphser.Checkpoint.SchemaContract` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Deterministic persistence.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize restore divergence and compatibility errors.
### 0.B Reproducibility Contract
- Replayable given `(checkpoint_hash, checkpoint_header_hash, schema_version, replay_token)`.
### 0.C Numeric Policy
- Binary blobs and scalar metadata are typed and deterministic.
### 0.D Ordering and Tie-Break Policy
- Canonical field order for serialization.
### 0.E Parallel, Concurrency, and Reduction Policy
- Checkpoint writes are atomic and serialized deterministically.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for checkpoint metadata and hashes.
### 0.G Operator Manifest
- `Glyphser.Checkpoint.ValidateSchema`
- `Glyphser.Checkpoint.Serialize`
- `Glyphser.Checkpoint.Restore`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Fully-qualified checkpoint fields by subsystem.
### 0.I Outputs and Metric Schema
- Outputs: `(checkpoint_blob, restore_report)`.
- Metrics: `checkpoint_size_bytes`, `restore_time_ms`, `compatibility_level`.
- Completion status: `success | failed`.
### 0.J Spec Lifecycle Governance
- Breaking field changes require MAJOR bump.
### 0.K Failure and Error Semantics
- Abort on incompatible schema or hash mismatch.
### 0.L Input/Data Provenance
- Checkpoint records source run hash and manifest hash.

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
- checkpoint schema registry.
### I.B Inputs and Hyperparameters
- subsystem states and schema version.
### I.C Constraints and Feasible Set
- Valid if required fields and hashes match.
### I.D Transient Variables
- serialization buffers and restore diagnostics.
### I.E Invariants and Assertions
- round-trip serialize/restore invariance.

### II.F Checkpoint Record Layout (Concrete)
- Required fields:
  - `tenant_id:string`
  - `run_id:string`
  - `spec_version:string`
  - `checkpoint_schema_version:string`
  - `replay_token:bytes32`
  - `t:uint64`
  - `manifest_hash:bytes32`
  - `ir_hash:bytes32`
  - `trace_snapshot_hash:bytes32`
  - `sampler_config_hash:bytes32`
  - `tmmu_plan_hash:bytes32`
  - `backend_binary_hash:bytes32`
  - `checkpoint_merkle_root:bytes32`
  - `policy_bundle_hash:bytes32`
  - `determinism_profile_hash:bytes32`
  - `lockfile_hash:bytes32`
  - `toolchain_hash:bytes32`
  - `dependencies_lock_hash:bytes32`
  - `operator_contracts_root_hash:bytes32`
  - `runtime_env_hash:bytes32`
  - `code_commit_hash:bytes32`
- `lineage_root_hash:bytes32` (snapshot-at-checkpoint value; MUST match certificate lineage commitment for the finalized run branch that includes this checkpoint)
  - lineage consistency rule: `lineage_root_hash` MUST equal the deterministic lineage root recomputed from checkpoint-scoped lineage objects/artifacts referenced by this checkpoint snapshot.
  - `dp_enabled:bool`
  - `tensors_root_hash:bytes32` (empty-set rule: if no tensor shards, root is `CommitHash("tensors_root", [])` per hash identities below)
  - `optimizer_state_root_hash:bytes32` (empty-set rule: if no optimizer shards, root is `CommitHash("optimizer_root", [])` per hash identities below)
  - `rng_state_hash:bytes32`
  - `data_cursors_hash:bytes32`
  - `dp_accountant_state_hash?:bytes32`
  - `weights_manifest_hash?:bytes32`
  - `optimizer_manifest_hash?:bytes32`
  - `dp_accountant_manifest_hash?:bytes32`
  - `checkpoint_header_hash:bytes32`
  - `checkpoint_manifest_hash:bytes32`
  - `checkpoint_hash:bytes32`
  - `checkpoint_hash_prev?:bytes32`
- Hash identities (normative):
  - Hash typing:
    - `CommitHash(tag, data) = SHA-256(CBOR_CANONICAL([tag, data]))`
    - `ObjectDigest(obj) = SHA-256(CBOR_CANONICAL(obj))`
    - identities declared as `ObjectDigest` MUST NOT be reinterpreted as commitment hashes in certificates/release gates.
  - `checkpoint_header_cbor` is the canonical CBOR map of checkpoint header fields excluding `checkpoint_header_hash` itself.
  - `checkpoint_header_hash = ObjectDigest(checkpoint_header_cbor)`
  - `checkpoint_manifest_cbor` is a canonical CBOR map with keys:
    - `manifest_version:string`
    - `checkpoint_merkle_root:bytes32`
    - `shards:array<{path:string, sha256:bytes32, size_bytes:uint64}>` sorted by `path`
      - `path` normalization rule (normative): POSIX-style relative path only, forward slashes (`/`), no `.` or `..` segments, no repeated separators, and no leading slash.
    - `weights_manifest_hash?:bytes32`
    - `optimizer_manifest_hash?:bytes32`
    - `dp_accountant_manifest_hash?:bytes32`
    - `dataset_snapshot_id?:string`
    - `artifact_index_hash?:bytes32`
  - `checkpoint_manifest_hash = ObjectDigest(checkpoint_manifest_cbor)` where manifest commits all shard digests and `checkpoint_merkle_root`
  - `weights_manifest_hash = ObjectDigest(weights_manifest_cbor)`
  - `optimizer_manifest_hash = ObjectDigest(optimizer_manifest_cbor)`
  - `dp_accountant_manifest_hash = ObjectDigest(dp_accountant_manifest_cbor)`
  - `rng_state_hash = ObjectDigest(rng_state_cbor)`
  - `rng_state_cbor` canonical schema (normative):
    - `["rng_state", key_u32_0, key_u32_1, ctr_u32_0, ctr_u32_1, ctr_u32_2, ctr_u32_3]`
    - where key is Philox key `[u32;2]` and counter is `[u32;4]` in little-endian logical word order.
  - `data_cursors_hash = ObjectDigest(data_cursors_cbor)`
  - `tensors_root_hash` and `optimizer_state_root_hash` derivation (normative):
    - shard-leaf encoding shared with checkpoint Merkle leaves:
      - `leaf_i = SHA-256(CBOR_CANONICAL(["ckpt_shard", [shard_path_i, shard_sha256_i, shard_size_i]]))`,
    - `tensors_root_hash = SHA-256(CBOR_CANONICAL(["tensors_root", tensor_leaves_sorted]))` where `tensor_leaves_sorted` contains leaves for shards with normalized path prefix `tensors/`, sorted by `shard_path`,
    - `optimizer_state_root_hash =     - empty-set rule: if the filtered shard set is empty, root is `SHA-256(CBOR_CANONICAL(["tensors_root", []]))` for `tensors_root_hash` and `SHA-256(CBOR_CANONICAL(["optimizer_root", []]))` for `optimizer_state_root_hash`. empty, root is `CommitHash("tensors_root", [])` for tensors and `CommitHash("optimizer_root", [])` for optimizer state.
  - `checkpoint_hash = checkpoint_manifest_hash`
  - `dependencies_lock_hash = SHA-256(CBOR_CANONICAL(["deps_lock", [lockfile_hash, toolchain_hash, runtime_env_hash]]))`
  - `operator_contracts_root_hash = operator_registry_root_hash` from `docs/layer1-foundation/Operator-Registry-Schema.md`.
- `checkpoint_merkle_root` construction over shard payloads:
    - `leaf_i = SHA-256(CBOR_CANONICAL(["ckpt_shard", [shard_path_i, shard_sha256_i, shard_size_i]]))` with shards ordered by `shard_path`,
    - `parent = SHA-256(CBOR_CANONICAL(["ckpt_merkle_node", [left, right]]))`,
    - odd-leaf rule duplicates the last leaf.
    - empty-shard rule: if there are zero shards, `checkpoint_merkle_root = SHA-256(CBOR_CANONICAL(["ckpt_merkle_root", []]))`.
    - for streaming writes, root is computed only after all shard hashes are finalized; placeholder roots are invalid.
- Canonical absence encoding: optional fields are omitted (key absent), never encoded as `null`.
- Evolution rule: additive optional fields allowed in MINOR; required-field changes require MAJOR.
- Migration controls:
  - `migration_supported_from: array<string>`
  - `migration_operator: string`
  - `migration_invariants: array<string>`

### II.G Sharded/Streaming Container Format
- Container layout:
  - `checkpoint_manifest.cbor` (authoritative metadata + shard index)
  - `tensors/rank=<r>/shard=<k>.bin`
  - `optimizer/rank=<r>/state.bin` (optional)
  - `dp/accountant_state.cbor`
  - `rng/state.cbor`
  - `data/cursors.cbor`
  - `tmmu/plan.cbor`
  - `trace/link.cbor`
  - `artifacts/artifact_index.cbor`
- Integrity:
  - `checkpoint_manifest.cbor` includes per-shard hash list and Merkle root.
  - Full checkpoint hash is `checkpoint_manifest_hash`.
  - Binding rule:
    - `weights_manifest_hash` must hash to a manifest whose content-addressed entries jointly hash to `tensors_root_hash`.
    - `optimizer_manifest_hash` must hash to a manifest whose entries jointly hash to `optimizer_state_root_hash`.
    - `dp_accountant_manifest_hash` must hash to canonical accountant blobs that hash to `dp_accountant_state_hash` (when DP enabled).
- Atomicity protocol:
  - Local FS: write to temp path, `fsync(file)`, `rename(temp, final)`, `fsync(directory)`.
  - Object stores: write immutable checkpoint objects by content hash; finalize via conditional pointer publish (create-if-absent generation precondition).
  - crash-consistency guarantee: either previous checkpoint remains valid or new checkpoint pointer is fully published; partial writes are invalid.
- Restore semantics:
  - supports full restore and deterministic partial restore by shard subset when declared by policy.

### II.H Partial Restore Matrix (Normative)
- Training restore requires: model params, optimizer state, RNG states, data cursors, TMMU plan.
- If `dp_enabled=true` in checkpoint header and committed manifest/config, DP accountant state is additionally required; if `dp_enabled=false`, DP accountant fields must be absent (not null).
- Eval/infer partial restore may use: model params + minimal runtime config.
- Any partial restore must emit `restore_profile_id` and trace record.
- Restore precondition: manifest DP enablement MUST match checkpoint `dp_enabled`; mismatch is deterministic failure.
- Restore precondition: checkpoint `operator_contracts_root_hash` MUST match current runtime `operator_contracts_root_hash`; otherwise abort or execute declared deterministic registry migration path before restore.
- Restore precondition: recomputed `tmmu_plan_hash` from current IR/execution order MUST equal checkpoint `tmmu_plan_hash`; mismatch is deterministic failure (no implicit memory-plan adaptation).

### II.I Trace-Link Integrity (Normative)
- Checkpoint header must store:
  - `trace_snapshot_hash`
  - `checkpoint_hash_prev` (if checkpoint chaining enabled)
- In linear hash-chain mode, `trace_final_hash == trace_snapshot_hash` at checkpoint boundary.
- `trace/link.cbor` binds checkpoint to trace hash chain for tamper-evident replay.
- checkpoint manifest must include `dataset_snapshot_id` and `artifact_index_hash`.
- Canonical contract rule: the checkpoint header in this file is the authoritative shape and must match `docs/layer1-foundation/Data-Structures.md` `CheckpointHeader`.
- Restore identity rule: restore must abort deterministically on any mismatch in `{tenant_id, run_id, replay_token, trace_snapshot_hash, checkpoint_hash, manifest_hash, ir_hash, sampler_config_hash, tmmu_plan_hash, backend_binary_hash, determinism_profile_hash, policy_bundle_hash}`.

### II.J Run Commit Protocol (Normative)
- Commit is atomic via immutable-object writes plus a single commit-pointer object:
  1. write immutable content-addressed trace/checkpoint/lineage/certificate objects,
  2. compute and validate `trace_final_hash`, `checkpoint_hash`, `lineage_root_hash`, `certificate_hash`,
  3. publish `runs/<tenant_id>/<run_id>/COMMITTED` via conditional create-if-absent,
  4. pointer payload binds `{trace_final_hash, checkpoint_hash, lineage_root_hash, certificate_hash, wal_terminal_hash}`.
- Recovery rule after crash:
  - if COMMITTED pointer exists, validate referenced objects and finalize,
  - if pointer missing, treat run as uncommitted and recover deterministically from WAL.

### II.K Migration Certificate (Normative)
- Every schema migration must emit a signed migration certificate:
  - `from_schema_version`, `to_schema_version`,
  - `source_hash`, `target_hash`,
  - `migration_operator`, `migration_policy_hash`.
- Hash semantics:
  - `source_hash` = content hash of source object before migration,
  - `target_hash` = content hash of migrated output object after migration.
- Migration output must hash identically across conforming implementations.

---
## 3) Initialization
1. Load checkpoint schema.
2. Validate subsystem state snapshots.
3. Initialize canonical serializer.

---
## 4) Operator Manifest
- `Glyphser.Checkpoint.ValidateSchema`
- `Glyphser.Checkpoint.Serialize`
- `Glyphser.Checkpoint.Restore`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `Glyphser.Checkpoint.ValidateSchema`  
**Category:** IO  
**Signature:** `(state, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates checkpoint field presence/types.

**Operator:** `Glyphser.Checkpoint.Serialize`  
**Category:** IO  
**Signature:** `(validated_state -> checkpoint_blob)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** canonical deterministic serialization with hash attachment.

**Operator:** `Glyphser.Checkpoint.Restore`  
**Category:** IO  
**Signature:** `(checkpoint_blob -> restored_state, report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** validates hash/schema and reconstructs subsystem state.
If `checkpoint_schema_version` is older and listed in `migration_supported_from`, restore MUST apply deterministic `migration_operator` before state reconstruction.

**Operator:** `Glyphser.Checkpoint.Migrate`
**Category:** IO
**Signature:** `(old_checkpoint, from_version, to_version -> new_checkpoint)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** performs deterministic format migration while preserving logical checkpoint semantics and emitting migration certificate inputs.

---
## 6) Procedure
```text
1. ValidateSchema
2. Serialize
3. Restore (verification mode)
4. Return checkpoint_blob + restore_report
```

---
## 7) Trace & Metrics
### Logging rule
Checkpoint writes/restores emit deterministic records.
### Trace schema
- `run_header`: schema_version, source_hash
- `iter`: step, status
- `run_end`: checkpoint_hash, restore_status
### Metric schema
- `checkpoint_size_bytes`, `restore_time_ms`, `compatibility_level`
### Comparability guarantee
Comparable iff schema version and hash rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes deterministic ordering, schema completeness, round-trip invariance.
#### VII.B Operator test vectors (mandatory)
Checkpoint fixtures for valid/incompatible/corrupt cases.
#### VII.C Golden traces (mandatory)
Golden checkpoint hashes for baseline states.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for blob/hash and restored state.
#### VIII.B Allowed refactor categories
- serializer optimization preserving canonical bytes.
#### VIII.C Equivalence test procedure (mandatory)
Exact blob/hash compare + state equivalence.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- kernel, data, model, tmmu, dp states + metadata hashes.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- restored run must produce identical subsequent deterministic traces.
