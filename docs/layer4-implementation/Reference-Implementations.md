# Glyphser Reference Implementations Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.ReferenceImplementations`  
**Purpose (1 sentence):** Define canonical coding-level signatures and pseudocode for critical operators to eliminate implementation ambiguity.  
**Spec Version:** `Glyphser.Implementation.ReferenceImplementations` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Developer implementation guidance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.ReferenceImplementations`
- **Purpose (1 sentence):** Normative coding reference for critical operators.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize implementation drift across languages/backends.
### 0.B Reproducibility Contract
- Reference behavior must be replayable under identical inputs and policy hashes.
### 0.C Numeric Policy
- Critical arithmetic paths use binary64 and deterministic ordering.
### 0.D Ordering and Tie-Break Policy
- Stable deterministic index/rank ordering in all reference loops.
### 0.E Parallel, Concurrency, and Reduction Policy
- Reference code is sequential semantics; parallel implementations must be equivalent.
### 0.F Environment and Dependency Policy
- Reference implementations are language-agnostic and side-effect explicit.
### 0.G Operator Manifest
- `Glyphser.Data.NextBatch`
- `Glyphser.DifferentialPrivacy.Apply`
- `Glyphser.TMMU.PrepareMemory`
- `Glyphser.Replay.CompareTrace`
- `Glyphser.Certificate.EvidenceValidate`
### 0.H Namespacing and Packaging
- One reference module per operator family.
### 0.I Outputs and Metric Schema
- Outputs are canonical return structs per operator signature.
### 0.J Spec Lifecycle Governance
- Signature/algorithm-semantic changes are MAJOR.
### 0.K Failure and Error Semantics
- Error handling must map to `docs/layer1-foundation/Error-Codes.md` IDs only.
### 0.L Input/Data Provenance
- Inputs reference manifest/checkpoint/trace/schema hashes.

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
- none; references are pure semantic templates.
### I.B Inputs and Hyperparameters
- operator-specific typed inputs.
### I.C Constraints and Feasible Set
- valid only for schema-valid inputs.
### I.D Transient Variables
- local deterministic work buffers.
### I.E Invariants and Assertions
- signatures and side-effects must match `docs/layer1-foundation/API-Interfaces.md`.

### II.F Canonical Function Signatures (Normative)
- `Glyphser.Data.NextBatch(dataset_key, world_size, rank, stage_type, cursor_in) -> (indices, cursor_next, metrics)`
- `Glyphser.DifferentialPrivacy.Apply(gradients, dp_config, t, state) -> (noisy_gradients, state_next, metrics)`
- `Glyphser.TMMU.PrepareMemory(ir_dag, execution_order, mode, arena_config) -> (tensor_map, metrics)`
- `Glyphser.Replay.CompareTrace(trace_a, trace_b, replay_mode) -> divergence_report`
- `Glyphser.Certificate.EvidenceValidate(manifest, trace, checkpoint, replay_ctx) -> validation_report`
- All signatures must be derived from `contracts/operator_registry.cbor`; manual signature drift is forbidden.
- Alias note: short helper names may appear in pseudocode, but normative identity is always the fully-qualified operator id.

### II.G Normative Reference Pseudocode (Required)
- `CBOR_CANONICAL(value)`:
  - encode using `docs/layer1-foundation/Canonical-CBOR-Profile.md` (definite lengths, no duplicate keys, key order by `(len(encoded_key), encoded_key)`).
  - reject non-UTF8 text keys and forbidden float values in signed payloads.
- `ResolveDigestRef(digest_ref, digest_catalog)`:
  - if tail matches `^[0-9a-f]{64}$`, return inline bytes32 digest.
  - else resolve label in `digest_catalog`; abort with `CONTRACT_VIOLATION` if missing.
- `TraceRecordHashChain(normalized_records)`:
  - `h = SHA-256(CBOR_CANONICAL(["trace_chain", []]))`
  - for each record in canonical order:
    - `r = SHA-256(CBOR_CANONICAL(record))`
    - `h = SHA-256(CBOR_CANONICAL(["trace_chain", [h, r]]))`
  - return `h` as `trace_final_hash` in linear-chain mode.
- `WalChainAndFinalize(records)`:
  - compute each `record_hash_i = SHA-256(CBOR_CANONICAL(["wal_record", [tenant_id, run_id, wal_seq_i, record_type_i, prev_record_hash_i, payload_i]]))`.
  - terminal `FINALIZE` record hash is `commit_record_hash`.
  - `wal_terminal_hash = commit_record_hash`.
- `PublishCommitPointer(pointer_payload)`:
  - payload must include `{trace_final_hash, checkpoint_hash, lineage_root_hash, execution_certificate_hash, wal_terminal_hash}`.
  - publish `runs/<tenant_id>/<run_id>/COMMITTED` via conditional create-if-absent.
  - if object exists, compare payload hash; mismatch is deterministic failure.

---
## 3) Initialization
1. Load typed schemas.
2. Validate operator signatures.
3. Bind deterministic helper primitives.

---
## 4) Operator Manifest
- `Glyphser.Implementation.Ref.NextBatch`
- `Glyphser.Implementation.Ref.ApplyDP`
- `Glyphser.Implementation.Ref.PrepareMemory`
- `Glyphser.Implementation.Ref.ReplayCompare`
- `Glyphser.Implementation.Ref.EvidenceValidate`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Implementation.Ref.NextBatch`  
**Category:** Implementation  
**Signature:** `(dataset_key, world_size, rank, stage_type, cursor_in -> indices, cursor_next, metrics)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical sampling pseudocode consistent with `docs/layer2-specs/Data-NextBatch.md`.

**Operator:** `Glyphser.Implementation.Ref.ApplyDP`  
**Category:** Implementation  
**Signature:** `(gradients, dp_config, t, state -> noisy_gradients, state_next, metrics)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic control / stochastic noise per RNG contract  
**Definition:** canonical DP pseudocode consistent with `docs/layer2-specs/DifferentialPrivacy-Apply.md`.

**Operator:** `Glyphser.Implementation.Ref.PrepareMemory`  
**Category:** Implementation  
**Signature:** `(ir_dag, execution_order, mode, arena_config -> tensor_map, metrics)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** canonical injective arena-offset planner pseudocode.

**Operator:** `Glyphser.Implementation.Ref.ReplayCompare`
**Category:** Implementation
**Signature:** `(trace_a, trace_b, replay_mode -> divergence_report)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** canonical comparator pseudocode aligned with `docs/layer2-specs/Replay-Determinism.md`.

**Operator:** `Glyphser.Implementation.Ref.EvidenceValidate`
**Category:** Implementation
**Signature:** `(manifest, trace, checkpoint, replay_ctx -> validation_report)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** canonical evidence-link validation pseudocode aligned with `docs/layer2-specs/Execution-Certificate.md`.

---
## 6) Procedure
```text
1. Validate schemas and signatures.
2. Execute operator-specific reference procedure.
3. Emit canonical outputs and metrics.
4. Verify expected side-effects set.
```

---
## 7) Trace & Metrics
### Logging rule
- reference runs emit deterministic debug traces for compare-only use.
### Trace schema
- `run_header`: operator, signature_digest
- `iter`: step, local_state_hash
- `run_end`: output_hash
### Metric schema
- `steps`, `deterministic_checks_passed`
### Comparability guarantee
- comparable iff signatures, inputs, and policies are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- no hidden globals, total state updates, deterministic ordering.
#### VII.B Operator test vectors (mandatory)
- each reference function must pass catalog vectors from `docs/layer3-tests/Test-Vectors-Catalog.md`.
#### VII.C Golden traces (mandatory)
- golden output hashes per reference operator.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for outputs and side-effects on deterministic paths.
#### VIII.B Allowed refactor categories
- language/runtime rewrites preserving signature and semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare against golden vectors and output hashes.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- optional local reference-state snapshots for debug replay.
### Serialization
- deterministic CBOR.
### Restore semantics
- restored reference state yields identical outputs.
