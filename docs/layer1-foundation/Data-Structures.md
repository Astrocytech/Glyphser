# Glyphser Data Structure Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.DataStructureContract`  
**Purpose (1 sentence):** Define deterministic canonical runtime data structures for kernel, model IR, TMMU, data, and DP modules.  
**Spec Version:** `Glyphser.Implementation.DataStructureContract` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Type/layout specification for interoperable deterministic execution.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.DataStructureContract`
- **Purpose (1 sentence):** Canonical data-structure definitions.
- **Spec Version:** `Glyphser.Implementation.DataStructureContract` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Runtime type contracts.

### 0.A Objective Semantics
- This contract defines canonical structure schemas and validation rules (not an optimization objective).
- Primary guarantee: exact type/field consistency across modules.
- Scope split (normative):
  - **Schema layer:** declaration language and schema-registry validation.
  - **Instance layer:** validation and canonical serialization of runtime data records against declared schemas.

### 0.B Reproducibility Contract
- Seed space/PRNG inherited by consuming operators.
- Randomness locality: none in structure contract.
- Replay guarantee: structure version + canonical schema hash sufficient for replay compatibility.
- `replay_token` is constrained in this contract as opaque `bytes32`; generation is defined by replay/runtime contracts.
- Hash primitive for all `bytes32` commitment fields in this document is `SHA-256` over canonical CBOR preimages unless a field definition explicitly overrides it.

### 0.C Numeric Policy
- Numeric scalar kinds are explicit (`uint64`, `float64`, etc.).
- NaN/Inf allowances must be declared by consuming operator.
- Approx-equality: N/A (schema exactness).

### 0.D Ordering and Tie-Break Policy
- Field ordering is canonical and deterministic.
- Map-like structures require sorted key serialization.

### 0.E Parallel, Concurrency, and Reduction Policy
- Structure validation is deterministic and side-effect free.

### 0.F Environment and Dependency Policy
- Reference runtime: any deterministic schema validator.
- Determinism level: `BITWISE` for serialized schema hash.

### 0.G Operator Manifest
- `Glyphser.Implementation.ValidateSchemaDecl`
- `Glyphser.Implementation.ValidateInstance`
- `Glyphser.Implementation.ValidateStruct`
- `Glyphser.Implementation.SerializeCanonical`
- `Glyphser.Implementation.ComputeStructHash`
- `Glyphser.Error.Emit`
- Compatibility note: `Glyphser.Implementation.ValidateStruct` is a compat alias to schema validation.

### 0.H Namespacing and Packaging
- Structure names are namespaced by subsystem.

### 0.I Outputs and Metric Schema
- Outputs:
  - schema path: `(schema_validation_report, schema_canonical_bytes, schema_hash)`
  - instance path: `(instance_validation_report, instance_canonical_bytes, instance_hash)`
- Metrics: `struct_count`, `field_count`, `violations`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Breaking field deletion/rename/type change => MAJOR.
- Additive backward-compatible field => MINOR.
- Structure evolution policy: compatibility decisions are made at this contract version level; per-structure `StructDecl.version` is metadata for migrations and tooling.

### 0.K Failure and Error Semantics
- Abort-only; deterministic failure records.

### 0.L Input/Data Provenance
- Schema source must be version-tagged and hashable.

---

### 0.Z EQC Mandatory Declarations Addendum
- Seed/PRNG declarations: N/A in this contract (inherited from consuming operators).
- Numeric-kernel/transcendental declarations: N/A in this contract (inherited from consuming operators).
- Determinism declaration: BITWISE for canonical bytes/hash outputs in this contract.
- Error-trace declaration: inherited from `Error-Codes.md` and consuming operators.
- Scope declaration: this document is limited to structure typing, canonical serialization, and deterministic validation.

## 2) System Model

### I.A Persistent State
- `struct_registry: map<name, schema>`.

### I.B Inputs and Hyperparameters
- canonical structure declarations.

### I.C Constraints and Feasible Set
- Unconstrained, validity defined by exact schema rules.

### I.D Transient Variables
- validation diagnostics.

### I.E Invariants and Assertions
- unique structure names and stable field ordering.

### II.E Structure Declaration Language (Normative)
- Canonical declaration meta-model:
  - `StructDecl = {struct_name:string, version:string, fields:array<FieldDecl>, required_fields:array<string>, allow_additional_fields:bool}`
  - `FieldDecl = {name:string, type:string, required:bool, default?:diagnostics_scalar, constraints?:map<string,string>}`
- Type grammar (closed set for this contract):
  - primitive: `uint32|uint64|int64|float64|bool|string|bytes|bytes32|bytes64`
  - composed: `array<T> | map<string,T> | enum(...)`
- `diagnostics_scalar = bool|int64|uint64|float64|string|bytes`
- Enum representation rule:
  - `enum(...)` values are serialized as UTF-8 strings equal to the declared symbol names.
  - allowed symbols are exactly those listed inside `enum(...)` (or explicitly referenced by external enum contract).
- Validation rules:
  - each `required_fields` entry MUST match a declared field name,
  - per-field `required` is normative for instance-validation requiredness; `required_fields` is metadata and MUST equal the set of fields with `required=true`,
  - unknown type tokens are invalid,
  - when `allow_additional_fields=false`, undeclared fields are invalid,
  - default compatibility checks:
    - numeric primitive defaults MUST be representable in the declared numeric type/range,
    - `bytes32`/`bytes64` defaults MUST have exact required length,
    - `enum(...)` defaults MUST match a declared symbol,
    - fields with composed types (`array<T>`, `map<string,T>`) MUST NOT declare defaults.
- Instance validation rule:
  - every instance validation MUST identify the target `StructDecl.struct_name` + `version` and validate required fields/types/constraints against that declaration.
- Optionality encoding rule:
  - `FieldDecl.required` is the sole optionality indicator.
  - absent optional fields MUST be omitted (not encoded as `null`).
  - backward-compat declarations using `optional<T>` type aliases MUST be normalized to `required=false` + base type `T`; conflicting declarations are invalid.
- Default semantics:
  - `FieldDecl.default` MAY be applied by instantiation tooling for convenience.
  - validators and canonical serializers MUST NOT auto-materialize omitted fields from defaults in commitment paths.
- Constraints semantics:
  - `constraints` defaults to empty map when omitted.
  - recognized keys are schema-defined validation keys (for example `min`, `max`, `regex`, `max_len`); unknown keys are invalid unless explicitly allowed by consuming mode.

### II.F Concrete Structure Layouts
- Operator-level enums (`purity_class`, `side_effect`) are authoritative in `docs/layer1-foundation/Operator-Registry-Schema.md` and `docs/layer1-foundation/API-Interfaces.md` and are intentionally not redefined here.
- `privacy_class = PUBLIC | INTERNAL | CONFIDENTIAL`
- `redaction_mode = NONE | HMAC_SHA256_V1`
- `metric_aggregation = sum | mean | min | max | quantile`
- `TraceIterRecord` (CBOR map): `{kind:"ITER", t:uint64, stage_id:string, operator_id:string, operator_seq:uint64, rank:uint32, status:string, replay_token:bytes32, rng_offset_before?:uint64, rng_offset_after?:uint64, dp_accountant_state_hash?:bytes32, sampler_config_hash?:bytes32, tmmu_plan_hash?:bytes32, determinism_profile_hash?:bytes32, state_fp?:bytes32, functional_fp?:bytes32, trace_extensions?:map<string,diagnostics_scalar>, privacy_class:privacy_class}`.
- `TraceRunHeader`: `{kind:"RUN_HEADER", schema_version:string, tenant_id:string, run_id:string, replay_token:bytes32, task_type:string, world_size:uint32, backend_binary_hash:bytes32, driver_runtime_fingerprint_hash:bytes32, policy_bundle_hash:bytes32, monitor_policy_hash:bytes32, operator_contracts_root_hash:bytes32, policy_gate_hash?:bytes32, authz_decision_hash?:bytes32, redaction_mode:redaction_mode, redaction_key_id?:string, redaction_policy_hash?:bytes32, hash_gate_M:uint64, hash_gate_K:uint64}`.
  - `hash_gate_M`/`hash_gate_K` define deterministic hash-gated trace sampling parameters; invariant `0 < M` and `0 <= K <= M`.
  - `H` is the unsigned big-endian integer interpretation of `SHA-256(CBOR_CANONICAL([replay_token, [t, operator_seq, rank]]))`.
- `TracePolicyGateVerdictRecord`: `{kind:"POLICY_GATE_VERDICT", t:uint64, policy_gate_hash:bytes32, transcript_hash:bytes32}`.
- `TraceCheckpointCommitRecord`: `{kind:"CHECKPOINT_COMMIT", t:uint64, checkpoint_hash:bytes32, checkpoint_header_hash:bytes32, checkpoint_merkle_root:bytes32, trace_snapshot_hash:bytes32}`.
- `TraceCertificateInputsRecord`: `{kind:"CERTIFICATE_INPUTS", t:uint64, certificate_inputs_hash:bytes32}`.
- `TraceRunEndRecord`: `{kind:"RUN_END", status:string, final_state_fp:bytes32, trace_final_hash:bytes32}`.
- `TraceErrorRecord`: `{kind:"ERROR", t:uint64, rank:uint32, failure_code:string, failure_operator:string, replay_token:bytes32, diagnostics_hash:bytes32}`.
- `TraceRecord`: tagged union of `TraceRunHeader` + `TraceIterRecord` + `TracePolicyGateVerdictRecord` + `TraceCheckpointCommitRecord` + `TraceCertificateInputsRecord` + `TraceRunEndRecord` + `TraceErrorRecord`.
- `CheckpointHeader`: `{tenant_id:string, run_id:string, spec_version:string, replay_token:bytes32, t:uint64, manifest_hash:bytes32, ir_hash:bytes32, trace_final_hash:bytes32, sampler_config_hash:bytes32, data_access_plan_hash?:bytes32, tmmu_plan_hash:bytes32, backend_binary_hash:bytes32, checkpoint_merkle_root:bytes32, checkpoint_header_hash:bytes32, checkpoint_manifest_hash:bytes32, checkpoint_hash:bytes32, policy_bundle_hash:bytes32, determinism_profile_hash:bytes32, lockfile_hash:bytes32, toolchain_hash:bytes32, dependencies_lock_hash:bytes32, operator_contracts_root_hash:bytes32, runtime_env_hash:bytes32, code_commit_hash:bytes32, lineage_root_hash:bytes32, tensors_root_hash:bytes32, optimizer_state_root_hash:bytes32, dp_accountant_state_hash?:bytes32}`.
- `ErrorRecord`: `{code_id:string, numeric_code:uint32, severity:enum(FATAL|ERROR|WARN), subsystem:string, t:uint64, rank:uint32, failure_operator:string, replay_token:bytes32, message:string, retryable:bool, diagnostics?:map<string,diagnostics_scalar>, privacy_class:privacy_class}`.
- `diagnostics` scalar contract (normative):
  - allowed scalar leaves are `bool|int64|uint64|float64|string|bytes`,
  - `float64` values in diagnostics MUST be finite (`NaN/Inf` forbidden),
  - keys are UTF-8 strings and MUST be unique.
- `MonitorEvent`: `{tenant_id:string, run_id:string, model_version_id:string, window_id:string, metric_name:string, metric_value:float64, privacy_class:privacy_class}`.
- `MetricSchema`: `{metric_name:string, scalar_type:enum(float64|int64|bool|string), aggregation:metric_aggregation, quantile_p?:float64, window_policy:string, privacy_class:privacy_class}`.
  - `quantile_p` is required iff `aggregation=quantile` and MUST satisfy `0 < quantile_p <= 1`.
- `PipelineTransitionRecord`: `{tenant_id:string, job_id:string, attempt_id:uint32, transition_seq:uint64, idempotency_key:bytes32, from_state:string, to_state:string, status:string, diagnostics?:map<string,diagnostics_scalar>}`.
- `ResourceLedgerRecord`: `{tenant_id:string, run_id:string, t:uint64, bytes_allocated:uint64, peak_bytes:uint64, io_bytes_read:uint64, io_bytes_written:uint64, gpu_time_ms:uint64, cpu_time_ms:uint64, quota_decision:string, quota_policy_hash:bytes32}`.
- Scope partitioning:
  - **Core structure set (required):** `Trace*Record`, `CheckpointHeader`, `ErrorRecord`, `StructDecl`, `FieldDecl`.
  - **Extension structure set (optional modules):** `MonitorEvent`, `MetricSchema`, `PipelineTransitionRecord`, `ResourceLedgerRecord`.
  - If extension structures are used, they are contract-bound by this same canonical serialization profile.
- Alignment policy for binary layouts: applies to in-memory/native struct layouts only; it does not affect canonical CBOR wire encoding. Fields should align to natural size for native runtime efficiency; packed representation is forbidden for cross-language in-memory ABI payloads.
- Registry format (normative): `struct_registry: map<string, StructDecl>`; `ValidateSchemaDecl` validates declarations against this meta-model.
- Checkpoint hash preimage rule (normative):
  - `checkpoint_header_hash = SHA-256(CBOR_CANONICAL(CheckpointHeader excluding fields {checkpoint_header_hash, checkpoint_hash}))`
  - `checkpoint_hash = SHA-256(CBOR_CANONICAL(["checkpoint_commit", [checkpoint_header_hash, checkpoint_manifest_hash, checkpoint_merkle_root]]))`
  - Stored `checkpoint_header_hash` and `checkpoint_hash` are derived outputs, never recursive inputs.

### II.G Canonical Serialization v1 (Normative)
- All contract-critical hashes/signatures must be computed over canonical CBOR bytes only.
- Hash identity classes:
  - `CommitHash(domain_tag, data_object) = SHA-256(CBOR_CANONICAL([domain_tag, data_object]))` (domain-separated commitment/signature identity).
  - `ObjectDigest(data_object) = SHA-256(CBOR_CANONICAL(data_object))` (plain object digest, no domain separation).
  - Every hash field in this contract and consuming contracts MUST declare which class it uses; values are not interchangeable across classes.
- Serialization domains:
  - **Schema serialization:** canonical CBOR of `StructDecl` / registry objects.
  - **Instance serialization:** canonical CBOR of runtime records conforming to a declared `StructDecl`.
- Canonicalization rules:
  - map keys ordered by `(len(CBOR_ENCODE(key)), CBOR_ENCODE(key))` as defined in `docs/layer1-foundation/Canonical-CBOR-Profile.md`,
  - integers encoded in shortest canonical form,
  - signed fields must encode floats as IEEE-754 binary64 only,
  - `NaN` and `Inf` are forbidden in signed/hash-critical payloads unless explicitly normalized by operator contract,
  - strings must be valid UTF-8; non-NFC forms are invalid for signed payloads when the consuming contract requires NFC validity,
  - fixed-length digests (`bytes32`) must be exactly 32 bytes.
- Domain separation labels (for chained hashes/signatures) must be explicit CBOR string tags in the hashed tuple.
- Redaction determinism rule:
  - redaction is applied before canonical serialization when enabled by consuming contracts,
  - redacted values MUST be deterministic transforms defined by `redaction_mode`/policy (e.g., keyed HMAC digest replacement),
  - resulting redacted structure is the committed/serialized payload.

### II.H Replay Token Binding (Normative in this contract)
- `replay_token` type is `bytes32`.
- Inclusion rule: when a structure includes `replay_token`, it MUST be present and serialized exactly as 32-byte CBOR byte string.
- Generation rule is defined in `docs/layer2-specs/Replay-Determinism.md`; this document does not redefine token derivation.

---

## 3) Initialization

1. Load structure declarations.
2. Canonicalize field order.
3. Build registry.

---

## 4) Operator Manifest

- `Glyphser.Implementation.ValidateSchemaDecl`
- `Glyphser.Implementation.ValidateInstance`
- `Glyphser.Implementation.ValidateStruct`
- `Glyphser.Implementation.SerializeCanonical`
- `Glyphser.Implementation.ComputeStructHash`
- `Glyphser.Error.Emit`
- Compatibility note: `Glyphser.Implementation.ValidateStruct` aliases `Glyphser.Implementation.ValidateSchemaDecl`.

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

**Operator:** `Glyphser.Implementation.ValidateStruct`  
**Category:** IO  
**Signature:** `(registry -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** compatibility alias for `Glyphser.Implementation.ValidateSchemaDecl`.  
**Preconditions / Postconditions:** registry loaded.  
**Edge cases:** optional fields and nested maps.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Complexity note:** O(total_fields).  
**Failure behavior:** deterministic schema failures.  
**Dependencies:** canonical schema parser.  
**Test vectors:** valid/invalid schema fixtures.

**Operator:** `Glyphser.Implementation.ValidateSchemaDecl`  
**Category:** IO  
**Signature:** `(registry -> schema_validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates schema declarations (`StructDecl`/`FieldDecl`) and registry invariants.  
**Preconditions / Postconditions:** registry loaded.  
**Edge cases:** optional fields and nested maps.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Complexity note:** O(total_fields).  
**Failure behavior:** deterministic schema failures.  
**Dependencies:** canonical schema parser.  
**Test vectors:** valid/invalid schema fixtures.

**Operator:** `Glyphser.Implementation.ValidateInstance`  
**Category:** IO  
**Signature:** `(instance, struct_name, struct_version, registry -> instance_validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates runtime instance payload against a declared schema in the registry.
**Preconditions / Postconditions:** target schema exists and is valid.
**Edge cases:** optional-field omission, unknown fields, constraint violations.
**Numerical considerations:** finite-float checks where required by target schema.
**Ordering/tie handling:** N/A.
**Complexity note:** O(instance_fields + schema_fields).
**Failure behavior:** deterministic validation failure with stable diagnostics.
**Dependencies:** canonical schema parser.
**Test vectors:** valid/invalid instance fixtures.

**Operator:** `Glyphser.Implementation.SerializeCanonical`  
**Category:** IO  
**Signature:** `(object -> canonical_bytes)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** deterministic canonical encoding for hashing and checkpointing (schema objects or runtime instances).  
**Preconditions / Postconditions:** input object validated in its domain (schema or instance).  
**Edge cases:** empty registry/object.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** sorted names then fields.  
**Complexity note:** O(object_size).  
**Failure behavior:** abort on serialization mismatch.  
**Dependencies:** serializer backend.  
**Test vectors:** golden serialized bytes.

**Operator:** `Glyphser.Implementation.ComputeStructHash`  
**Category:** IO  
**Signature:** `(canonical_bytes -> hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes deterministic structure hash.  
**Preconditions / Postconditions:** canonical bytes only.  
**Edge cases:** zero-length bytes.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Complexity note:** O(bytes).  
**Failure behavior:** abort on hash failure.  
**Dependencies:** hash function.  
**Test vectors:** fixed byte->hash vectors.

---

## 6) Procedure

```text
Schema path:
1. ValidateSchemaDecl(registry)
2. SerializeCanonical(registry)
3. ComputeStructHash(schema_canonical_bytes)
4. Return schema_validation_report + schema_canonical_bytes + schema_hash

Instance path:
1. ValidateInstance(instance, struct_name, struct_version, registry)
2. SerializeCanonical(instance)
3. ComputeStructHash(instance_canonical_bytes)
4. Return instance_validation_report + instance_canonical_bytes + instance_hash
```

---

## 7) Trace & Metrics

### Logging rule
Emit deterministic structure validation and hash records.

### Trace schema
- `run_header`: `TraceRunHeader`
- `iter`: `TraceIterRecord` (and optional typed records from `TraceRecord` union)
- `run_end`: `TraceRunEndRecord`
- `error`: `TraceErrorRecord`

### Metric schema
- `struct_count`, `field_count`, `violations`

### Comparability guarantee
Comparable iff schema definitions and canonical serializer are identical.

---

## 8) Validation

#### A. Lint rules (mandatory)
Passes determinism, completeness, ordering, no hidden globals.

#### B. Operator test vectors (mandatory)
Schema fixtures and canonical serialization vectors.
- Minimum vector classes:
  - optional-field omission vs explicit null (when schema permits),
  - duplicate-key rejection,
  - finite/non-finite diagnostics scalar checks,
  - checkpoint hash derivation preimage exclusion (`checkpoint_header_hash`, `checkpoint_hash`),
  - trace extension map canonical ordering.

#### C. Golden traces (mandatory)
Golden hashes for canonical registries.
- Authoritative vector index: `docs/layer3-tests/Test-Vectors-Catalog.md`.
- Missing or stale vectors are a contract violation for release builds.

---

## 9) Refactor & Equivalence

#### A. Equivalence levels
- E0 required.
- `E0` means byte-identical canonical bytes and identical hash outputs for identical logical structure declarations (aligned with `docs/layer2-specs/Replay-Determinism.md`).

#### B. Allowed refactor categories
- Parser/serializer refactor with identical bytes/hash output.

#### C. Equivalence test procedure (mandatory)
Compare report and final hash exactly.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- canonical schema bytes + hash.

### Serialization
- deterministic canonical CBOR.

### Restore semantics
- identical restored registry and hash.

### Normative dependencies
- `docs/layer1-foundation/Canonical-CBOR-Profile.md`
- `docs/layer1-foundation/Error-Codes.md`
- `docs/layer1-foundation/Operator-Registry-Schema.md`
- `docs/layer1-foundation/API-Interfaces.md`
- `docs/layer2-specs/Replay-Determinism.md`
- `docs/layer3-tests/Test-Vectors-Catalog.md`
- Release gate: all normative dependency documents above MUST exist in the same versioned artifact bundle for conformance.

### Embedded example fixture (illustrative, non-authoritative)
```yaml
StructDecl:
  struct_name: "ExampleRecord"
  version: "v1"
  fields:
    - { name: "id", type: "string", required: true }
    - { name: "count", type: "uint64", required: false, default: 0 }
  required_fields: ["id"]
  allow_additional_fields: false
```
