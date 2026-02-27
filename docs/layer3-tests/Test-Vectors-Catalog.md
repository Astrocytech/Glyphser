# Glyphser Test Vectors Catalog Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.VectorsCatalog`  
**Purpose (1 sentence):** Define authoritative operator-level input/output vectors and expected hashes/errors for deterministic conformance testing.  
**Spec Version:** `Glyphser.Test.VectorsCatalog` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Golden-vector governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.VectorsCatalog`
- **Purpose (1 sentence):** Canonical test vector registry.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize ambiguous test expectations across implementations.
### 0.B Reproducibility Contract
- vectors and expected outputs are content-addressed and immutable.
- replayable given `(vector_id, operator_id, implementation_version)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- expected numeric outputs include explicit dtype and tolerance class.
### 0.D Ordering and Tie-Break Policy
- vectors are ordered by `(operator_id, vector_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- suite merge order is deterministic lexical order.
### 0.F Environment and Dependency Policy
- vector files use canonical serialization and hashes.
### 0.G Operator Manifest
- `Glyphser.Test.VectorLoad`
- `Glyphser.Test.VectorExecute`
- `Glyphser.Test.VectorVerify`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `vectors/<operator>/<vector_id>.cbor`.
### 0.I Outputs and Metric Schema
- outputs: `(verification_report)` and mismatch diagnostics.
### 0.J Spec Lifecycle Governance
- vector content changes are MAJOR unless additive new vector IDs.
### 0.K Failure and Error Semantics
- mismatch emits deterministic error records.
### 0.L Input/Data Provenance
- each vector stores source-spec hash and operator signature digest.

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
- vector registry and golden hash index.
### I.B Inputs and Hyperparameters
- operator_id, vector_id, implementation target.
### I.C Constraints and Feasible Set
- vector must match declared operator signature digest.
### I.D Transient Variables
- run outputs, diff report.
### I.E Invariants and Assertions
- exact expected outputs for E0 fields.

### II.F Vector Record Schema (Normative)
- `operator_id:string`
- `vector_id:string`
- `input_payload_hash:bytes32`
- `expected_output_hash:bytes32`
- `expected_error_code?:string`
- `determinism_class: "E0" | "E1"`
- `signature_digest:bytes32`
- `canonical_encoding_version:string` (`CanonicalSerialization`)

### II.G Canonical Encoding Vector Set (Normative)
- Catalog must include vectors for canonical serialization and hashing:
  - canonical CBOR map key ordering,
  - float64 encoding edge cases,
  - fixed-length digest validation (`bytes32`),
  - domain-separated hash tuple examples.
- These vectors are mandatory for conformance of hashing/signature-related operators.

### II.H `vectors_catalog.cbor` Schema (Normative)
- Authoritative machine-readable artifact: `contracts/vectors_catalog.cbor`.
- Schema:
  - `catalog_version:string`
  - `operators: map<string, array<map>>`, where each vector map contains:
    - `vector_id:string`
    - `input_digest:digest_ref`
    - `expected_output_digest:digest_ref`
    - `expected_error_code?:string`
    - `determinism_class: "E0" | "E1"`
    - `signature_digest:digest_ref`
    - `notes?:string`
- Catalog hash:
  - `vectors_catalog_hash = SHA-256(CBOR_CANONICAL(vectors_catalog_map))`.

### II.I Minimum Baseline Vector Set (Normative)
- Required baseline vectors:
  - canonical CBOR map ordering edge cases (`len-first` ordering),
  - trace hash-chain over a 3-record sequence (`trace_chain`),
  - WAL chain plus terminal `FINALIZE` commit record hash,
  - `digest_ref` resolution (`sha256:<hex64>` inline and `sha256:<label>` lookup),
  - `NextBatch` deterministic sampling on at least two small datasets and one distributed shard case.

---
## 3) Initialization
1. Load vector registry.
2. Validate hash/index integrity.
3. Bind operator executor.

---
## 4) Operator Manifest
- `Glyphser.Test.VectorLoad`
- `Glyphser.Test.VectorExecute`
- `Glyphser.Test.VectorVerify`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Test.VectorLoad`
**Category:** Test
**Signature:** `(operator_id, vector_id -> expected_vector)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** loads canonical vector payload and expected outputs/errors by id.
**allowed_error_codes:** `VECTOR_NOT_FOUND`, `CONTRACT_VIOLATION`.

**Operator:** `Glyphser.Test.VectorExecute`
**Category:** Test
**Signature:** `(implementation, input_payload -> actual_output)`
**Purity class:** IO
**Determinism:** deterministic for identical implementation+input payload
**Definition:** executes the implementation against vector input payload.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `PRIMITIVE_UNSUPPORTED`, `EXECUTION_FAILURE`.

**Operator:** `Glyphser.Test.VectorVerify`  
**Category:** Test  
**Signature:** `(actual_output, expected_vector -> verify_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** verifies outputs/errors against canonical vector expectations.
**allowed_error_codes:** `VECTOR_MISMATCH`, `EXPECTED_ERROR_MISMATCH`, `CONTRACT_VIOLATION`.

---
## 6) Procedure
```text
1. VectorLoad(operator_id, vector_id)
2. VectorExecute(implementation, input_payload)
3. VectorVerify(actual, expected)
4. Emit verify_report
```

---
## 7) Trace & Metrics
### Logging rule
- every vector execution emits deterministic verification records.
### Trace schema
- `run_header`: operator_id, vector_id
- `iter`: step, status
- `run_end`: verify_status, mismatch_hash?
### Metric schema
- `passed`, `failed`, `mismatch_count`
### Comparability guarantee
- comparable iff vector payloads and signature digests match.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- no duplicate vector IDs per operator; required fields complete.
#### VII.B Operator test vectors (mandatory)
- self-test vectors for loader/executor/verifier.
#### VII.C Golden traces (mandatory)
- golden verify traces for representative vectors.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for verifier verdict and mismatch report.
#### VIII.B Allowed refactor categories
- storage/indexing changes preserving vector contents and IDs.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of verify_report on golden vectors.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- vector-run cursor and partial batch verification state.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed vector run yields identical final verify report.
