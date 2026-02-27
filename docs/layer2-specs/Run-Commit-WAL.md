# Glyphser Run Commit WAL Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Commit.RunCommitWAL`  
**Purpose (1 sentence):** Define deterministic write-ahead logging and recovery rules for atomic run commit of trace/checkpoint/lineage/certificate artifacts.  
**Spec Version:** `Glyphser.Commit.RunCommitWAL` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Crash-consistent artifact finalization.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Commit.RunCommitWAL`
- **Purpose (1 sentence):** Atomic, replayable run finalization.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: exact WAL replay and final artifact set equality.
- Invalid objective policy: partial-commit states are failures.
### 0.B Reproducibility Contract
- Replayable given `(wal_records, run_id, tenant_id)`.
### 0.C Numeric Policy
- Counters and sequence IDs use uint64.
- Counter overflow is forbidden: any increment that would exceed `2^64-1` MUST abort with `COUNTER_OVERFLOW`.
### 0.D Ordering and Tie-Break Policy
- WAL records are strictly ordered by `wal_seq`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Exactly one active commit writer per `(tenant_id, run_id)`.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE`.
### 0.G Operator Manifest
- `Glyphser.Commit.WALAppend`
- `Glyphser.Commit.WALRecover`
- `Glyphser.Commit.FinalizeRunCommit`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- WAL paths:
  - `wal/run_commit/<tenant_id>/<run_id>/records/<wal_seq>.cbor`
  - `runs/<tenant_id>/<run_id>/COMMITTED` (single canonical commit-pointer object)
### 0.I Outputs and Metric Schema
- Outputs: `(commit_status, commit_record_hash, wal_terminal_hash)`.
### 0.J Spec Lifecycle Governance
- WAL record shape changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on sequence gaps, duplicate terminal records, or hash mismatch.
### 0.L Input/Data Provenance
- All artifact IDs/hashes in WAL must be content-addressed.

---
## 2) System Model
### I.A Persistent State
- WAL append log and commit index.
### I.B Inputs and Hyperparameters
- temp artifact refs and final artifact refs.
### I.C Constraints and Feasible Set
- valid iff WAL sequence monotone and commit protocol complete.
### I.D Transient Variables
- recovery plan and validation diagnostics.
### I.E Invariants and Assertions
- exactly one committed terminal record per run.

### II.F WAL Record Schema (Normative)
- Required fields:
  - `tenant_id:string`
  - `run_id:string`
  - `wal_seq:uint64`
  - `record_type:enum("PREPARE","CERT_SIGNED","FINALIZE","ROLLBACK")`
  - `trace_tmp_hash?:bytes32`
  - `checkpoint_tmp_hash?:bytes32`
  - `lineage_tmp_hash?:bytes32`
  - `certificate_tmp_hash?:bytes32`
  - `trace_final_hash?:bytes32`
  - `checkpoint_final_hash?:bytes32`
  - `lineage_final_hash?:bytes32`
  - `certificate_final_hash?:bytes32`
  - `manifest_hash?:bytes32`
  - `policy_bundle_hash?:bytes32`
  - `operator_registry_hash?:bytes32`
  - `determinism_profile_hash?:bytes32`
  - `checkpoint_hash?:bytes32`
  - `lineage_root_hash?:bytes32`
  - `certificate_hash?:bytes32`
  - `commit_pointer_hash?:bytes32`
  - `prev_record_hash:bytes32`
  - `record_length_u32:uint32`
  - `record_crc32c:uint32`
  - `record_hash:bytes32`

WAL hash-chain rule:
- Define `wal_record_payload_i` as the canonical CBOR map of the WAL record with all present fields except `record_hash`.
- `record_hash_i = SHA-256(CBOR_CANONICAL(["wal_record", wal_record_payload_i]))`
- `commit_record_hash = record_hash` of the terminal `FINALIZE` WAL record.
- `wal_terminal_hash = commit_record_hash`.
- WAL framing integrity rule:
  - records are persisted as `[record_length_u32 | record_cbor_bytes | record_crc32c]`,
  - `record_length_u32` and `record_crc32c` are encoded in little-endian byte order,
  - `record_crc32c` uses CRC-32C (Castagnoli polynomial, RFC 3720),
  - `record_crc32c` is computed over `record_cbor_bytes`,
  - recovery MUST reject checksum mismatches and truncated trailing records as `WAL_CORRUPTION`.

Terminal commit record rule:
- `record_type="FINALIZE"` MUST include:
  - `trace_final_hash`, `checkpoint_hash`, `lineage_root_hash`, `certificate_hash`,
  - `manifest_hash`, `policy_bundle_hash`, `operator_registry_hash`, `determinism_profile_hash`.
- `CERT_SIGNED` record payload rule:
  - `record_type="CERT_SIGNED"` MUST include at least one of:
    - `certificate_tmp_hash` (pre-final certificate artifact), or
    - `certificate_final_hash` (finalized certificate artifact),
  - and SHOULD include `policy_bundle_hash` + `determinism_profile_hash` to bind signing context.

### II.G Recovery Rule (Normative)
- Deterministic `WALRecover` algorithm:
  1. Enumerate records for `(tenant_id, run_id)` by strictly ascending `wal_seq`.
  2. Validate continuity: first record MUST have `wal_seq=0`; each next record MUST increment by exactly 1.
  3. Validate framing/checksum for each record (`record_length_u32`, `record_crc32c`); detect and reject torn writes.
  4. Validate hash chain: for each record `i>0`, `prev_record_hash_i == record_hash_{i-1}`; recompute each `record_hash_i` from canonical payload and verify equality.
  5. If chain validation fails (gap, mismatch, duplicate terminal), abort with `WAL_CORRUPTION`.
  6. Determine terminal state from highest `wal_seq` record:
     - `FINALIZE`: verify all referenced final artifacts exist and hashes match; if valid, mark committed and return success.
     - `ROLLBACK`: ensure no final artifacts are visible via COMMITTED pointer; return rolled-back success.
     - non-terminal (`PREPARE` or `CERT_SIGNED`): execute deterministic rollback:
       - remove temp artifacts referenced by WAL (idempotent),
       - remove COMMITTED pointer if present and inconsistent,
       - append terminal `ROLLBACK` record if absent.
  7. Emit deterministic recovery report with status, terminal record hash, and any removed temp refs.

Canonical commit barrier:
- Write immutable content-addressed artifacts first.
- Publish a single commit-pointer object `runs/<tenant_id>/<run_id>/COMMITTED` via conditional create-if-absent.
- Commit pointer payload binds `{trace_final_hash, checkpoint_hash, lineage_root_hash, certificate_hash, wal_terminal_hash}`.
- WAL remains recovery evidence; COMMITTED pointer is the canonical visibility barrier.

---
## 3) Initialization
1. Open/create WAL stream.
2. Validate existing sequence continuity.
3. Initialize commit state machine.

---
## 4) Operator Manifest
- `Glyphser.Commit.WALAppend`
- `Glyphser.Commit.WALRecover`
- `Glyphser.Commit.FinalizeRunCommit`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Commit.WALAppend`  
**Category:** IO  
**Signature:** `(tenant_id, run_id, wal_record -> wal_state')`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** resolves run-scoped WAL path from `(tenant_id, run_id)`, then appends canonical record with monotone `wal_seq`.
Caller contract: `wal_record` MUST contain at least `record_type` plus required payload fields for that type; caller MUST NOT provide `wal_seq`, `prev_record_hash`, `record_hash`, `record_length_u32`, or `record_crc32c` (these are deterministically filled by the operator).

**Operator:** `Glyphser.Commit.WALRecover`  
**Category:** IO  
**Signature:** `(tenant_id, run_id -> recovery_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Executes II.G algorithm exactly using `(tenant_id, run_id)` to resolve `wal_stream` and `artifact_store` deterministically (tenant/run scoped namespace paths), validates sequence/hash-chain, then deterministically finalize-or-rollback with idempotent artifact handling and explicit corruption failure.

**Operator:** `Glyphser.Commit.FinalizeRunCommit`  
**Category:** IO  
**Signature:** `(tenant_id, run_id -> commit_status)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** resolves run-scoped commit context from `(tenant_id, run_id)`, verifies all referenced immutable artifacts and hashes, publishes commit pointer atomically, and returns deterministic terminal commit status.

---
## 6) Procedure
```text
0. WALRecover(tenant_id, run_id) on startup/resume
1. WALAppend(tenant_id, run_id, {record_type:"PREPARE"})
2. WALAppend(tenant_id, run_id, {record_type:"CERT_SIGNED", certificate_tmp_hash})
3. FinalizeRunCommit(tenant_id, run_id)
4. WALAppend(tenant_id, run_id, {record_type:"FINALIZE", trace_final_hash, checkpoint_hash, lineage_root_hash, certificate_hash, manifest_hash, policy_bundle_hash, operator_registry_hash, determinism_profile_hash})
```

---
## 7) Trace & Metrics
### Logging rule
- Every WAL transition emits deterministic trace records.
### Trace schema
- `run_header`: tenant_id, run_id
- `iter`: wal_seq, record_type, status
- `run_end`: commit_status, commit_record_hash
### Metric schema
- `wal_records`, `recovery_attempts`, `rollback_count`
### Comparability guarantee
- Comparable iff WAL schema and recovery rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- monotone sequence, single terminal state.
#### VII.B Operator test vectors (mandatory)
- crash-before-finalize, crash-after-cert, duplicate-finalize cases.
#### VII.C Golden traces (mandatory)
- golden commit and recovery traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for final commit status and committed artifact hashes.
#### VIII.B Allowed refactor categories
- storage backend changes preserving WAL semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of terminal WAL state and final artifacts.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- WAL cursor and last validated terminal record hash.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed commit/recovery produces identical terminal outcome.
