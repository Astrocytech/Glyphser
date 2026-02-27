# Glyphser Error Code Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Error.CodeRegistry`  
**Purpose (1 sentence):** Define a deterministic unified error taxonomy and emission contract across all Glyphser operators.  
**Spec Version:** `Glyphser.Error.CodeRegistry` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Error semantics and interoperability.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Error.CodeRegistry`
- **Purpose (1 sentence):** Unified deterministic error registry.
- **Spec Version:** `Glyphser.Error.CodeRegistry` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Error taxonomy governance.
### 0.A Objective Semantics
- This contract is a static taxonomy/validation contract (not an optimization objective).
- Primary comparison rule: exact `code_id` + `numeric_code` identity and deterministic schema validation.
### 0.B Reproducibility Contract
- Replayable given `(error_registry_version, failure_context_hash)`.
### 0.C Numeric Policy
- Error fields are typed; numeric values deterministic and explicit.
### 0.D Ordering and Tie-Break Policy
- Error code ordering by lexical code id.
### 0.E Parallel, Concurrency, and Reduction Policy
- Concurrent failures are all emitted as independent records.
- Any summary/aggregation views MUST order records deterministically by `(t, failure_operator, code_id)` and MUST NOT discard emitted records.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for emitted error records.
### 0.G Operator Manifest
- `Glyphser.Error.Emit`
- `Glyphser.Error.ValidateRecord`
- `Glyphser.Error.SerializeRecord`
### 0.H Namespacing and Packaging
- Error codes are global and unique.
### 0.I Outputs and Metric Schema
- Outputs: `(error_record, serialized_error)`.
- Metrics: `error_code_frequency`, `first_failure_t`.
- Completion status: `failed` (or `success` for validation-only runs).
### 0.J Spec Lifecycle Governance
- New code additions are MINOR; semantic changes/removals are MAJOR.
### 0.K Failure and Error Semantics
- Abort-only or structured depending on caller policy; record always deterministic.
### 0.L Input/Data Provenance
- Error records include replay token and operator provenance.

---
### 0.Z EQC Mandatory Declarations Addendum
- Not applicable in this document beyond deterministic record emission/validation declared above; stochastic and numeric-kernel clauses are inherited from producing operators.


## 2) System Model
### I.A Persistent State
- error code registry.
### I.B Inputs and Hyperparameters
- failure context and policy.
### I.C Constraints and Feasible Set
- registry uniqueness and schema validity constraints.
### I.D Transient Variables
- formatted error record.
### I.E Invariants and Assertions
- every emitted code exists in registry.

### II.F Error Registry (Authoritative)
| code_id | numeric_code | category | severity | retryable | deterministic_fields_required | message_template | remediation | version_introduced |
|---|---:|---|---|---|---|---|---|---|
| `CONTRACT_VIOLATION` | 1801 | runtime | FATAL | false | `t,failure_operator,replay_token` | `Contract violation in {failure_operator}` | Validate manifest/operator contracts | v1 |
| `INVALID_STAGE_TYPE` | 1802 | runtime | ERROR | false | `t,stage_id,replay_token` | `Invalid pipeline stage type` | Fix manifest pipeline stage type | v1 |
| `BATCH_SIZE_INCONSISTENT` | 1101 | data | ERROR | false | `t,dataset_key,replay_token` | `global_batch_size % world_size != 0` | Fix manifest batch/world_size | v1 |
| `INVALID_DATASET_KEY` | 1102 | data | ERROR | false | `t,dataset_key,replay_token` | `Dataset key not found in manifest` | Register dataset and fix key | v1 |
| `CARDINALITY_MISMATCH` | 1103 | data | FATAL | false | `t,dataset_key,registered_hash` | `Dataset cardinality does not match registered metadata` | Re-register immutable dataset metadata | v1 |
| `GLOBAL_POSITION_EXCEEDS_CARDINALITY` | 1104 | data | ERROR | false | `t,dataset_key,global_position,cardinality` | `Global position exceeds dataset cardinality` | Reset cursor or fix cardinality metadata | v1 |
| `API_SIGNATURE_MISMATCH` | 1001 | config | ERROR | false | `t,interface_id,schema_hash` | `API signature mismatch` | Regenerate bindings from interface contract | v1 |
| `API_SHAPE_MISMATCH` | 1002 | config | ERROR | false | `t,interface_id,payload_hash` | `API payload shape mismatch` | Fix request/response schema or caller payload | v1 |
| `API_TYPE_MISMATCH` | 1003 | config | ERROR | false | `t,interface_id,field_path` | `API payload type mismatch` | Align caller and schema scalar/object types | v1 |
| `PRIVACY_BUDGET_EXCEEDED` | 1401 | dp | FATAL | false | `t,failure_operator,cumulative_epsilon,target_epsilon` | `DP budget exceeded` | Increase noise/reduce steps | v1 |
| `INVALID_DP_CONFIG` | 1402 | dp | ERROR | false | `t,accountant,clipping_strategy` | `Invalid differential privacy configuration` | Fix DP hyperparameters and mode compatibility | v1 |
| `ACCOUNTANT_OVERFLOW` | 1403 | dp | FATAL | false | `t,accountant_type,state_hash` | `Privacy accountant overflow` | Switch to stable accountant grid or lower horizon | v1 |
| `ACCOUNTANT_DIVERGENCE` | 1404 | dp | FATAL | false | `t,accountant_type,state_hash` | `Privacy accountant diverged` | Use validated accountant settings | v1 |
| `NAN_IN_SIGMA` | 1405 | dp | FATAL | false | `t,sigma_map_hash` | `Sigma schedule contains NaN/Inf` | Clamp/validate scheduler outputs | v1 |
| `INVALID_GRADIENT` | 1406 | dp | ERROR | false | `t,grad_hash` | `Gradient tensor invalid for DP path` | Validate backward output and clipping inputs | v1 |
| `RNG_CONSUMPTION_VIOLATION` | 1407 | dp | FATAL | false | `t,failure_operator,rng_offset_before,rng_offset_after` | `RNG consumption contract violated` | Fix operator RNG declaration/usage | v1 |
| `ALIGNMENT_VIOLATION` | 1301 | tmmu | FATAL | false | `t,arena,logical_slot` | `Memory alignment violation` | Increase alignment or remap slot | v1 |
| `TMMU_ALLOCATION_FAILURE` | 1302 | tmmu | FATAL | false | `t,arena,peak_required_bytes` | `TMMU allocation failed` | Increase arena capacity or reduce footprint | v1 |
| `ALLOCATION_OVERFLOW` | 1303 | tmmu | FATAL | false | `t,arena,offset,size` | `Allocation offset overflow` | Reduce allocation size or split arenas | v1 |
| `ARENA_TOO_SMALL` | 1304 | tmmu | ERROR | false | `t,arena,capacity,required` | `Arena capacity insufficient` | Increase capacity or enable recomputation | v1 |
| `LIVENESS_CYCLE` | 1305 | tmmu | ERROR | false | `t,ir_hash,node_id` | `Liveness analysis cycle detected` | Fix IR DAG and liveness metadata | v1 |
| `INVALID_IR_SHAPES` | 1306 | tmmu | ERROR | false | `t,ir_hash,node_id` | `Invalid static shapes for allocation` | Provide complete static shape metadata | v1 |
| `ADDRESS_COLLISION` | 1307 | tmmu | FATAL | false | `t,arena,logical_slot` | `Virtual address collision` | Regenerate plan with valid injective mapping | v1 |
| `BACKEND_CONTRACT_VIOLATION` | 1601 | backend | FATAL | false | `t,backend_binary_hash,driver_runtime_fingerprint_hash,failure_operator` | `Backend failed determinism contract` | Use certified driver build | v1 |
| `INVALID_IR` | 1201 | model | ERROR | false | `t,ir_hash,node_id` | `Invalid IR structure` | Validate/repair IR before execution | v1 |
| `CYCLE_DETECTED` | 1202 | model | ERROR | false | `t,ir_hash,node_id` | `Cycle detected in IR DAG` | Fix graph topology | v1 |
| `SHAPE_MISMATCH` | 1203 | model | ERROR | false | `t,node_id,shape_in,shape_expected` | `Tensor shape mismatch during dispatch` | Fix model IR shapes or adapter mapping | v1 |
| `PRIMITIVE_UNSUPPORTED` | 1602 | backend | ERROR | false | `t,node_id,instr,backend_binary_hash` | `Backend primitive unsupported` | Implement primitive or choose compatible backend | v1 |
| `DISTRIBUTED_COMMUNICATION_FAILURE` | 1803 | distributed | FATAL | true | `t,world_size,collective_id` | `Deterministic collective failed or timed out` | Retry with stable network or fallback topology | v1 |
| `COUNTER_OVERFLOW` | 1804 | runtime | FATAL | false | `t,failure_operator,counter_name,counter_value` | `Monotone uint64 counter overflow detected` | Reduce run horizon or rotate run/checkpoint before overflow | v1 |
| `ATTESTATION_FAILURE` | 1701 | security | FATAL | false | `t,quote_hash,policy_bundle_hash` | `Attestation verification failed` | Rotate trust roots/quotes and re-attest | v1 |
| `INVALID_OBJECTIVE` | 1204 | model | FATAL | false | `t,failure_operator,objective_value` | `Objective invalid (NaN/Inf/out-of-contract)` | Fix loss/objective numeric path and policy guards | v1 |
| `REPLAY_DIVERGENCE` | 1901 | replay | FATAL | false | `t,field_path,replay_token` | `Replay divergence detected` | Re-run with captured profile and inspect first divergence event | v1 |
| `TRACE_CAP_EXCEEDED_MANDATORY` | 1501 | trace | FATAL | false | `t,run_id,trace_policy_hash` | `Trace cap exceeded for mandatory record kinds` | Raise trace caps or reduce optional sampling load | v1 |
| `WAL_CORRUPTION` | 1502 | trace | FATAL | false | `t,run_id,wal_seq,record_hash` | `WAL chain corrupted or non-contiguous` | Rebuild WAL from durable snapshot or rollback run | v1 |
| `BASELINE_MISSING` | 1503 | trace | ERROR | false | `t,window_id,baseline_ref` | `Monitoring baseline artifact/window missing or invalid` | Register/fix baseline artifact and retry deterministic drift evaluation | v1 |

Numeric range reservation:
- 1000-1099 config/schema
- 1100-1199 data/sampler
- 1200-1299 modelir/executor/objective
- 1300-1399 tmmu/memory
- 1400-1499 differential privacy
- 1500-1599 trace/checkpoint
- 1600-1699 backend
- 1700-1799 security
- 1800-1899 distributed/runtime
- 1900-1999 replay/determinism

Lint invariant:
- Build/test must fail if any referenced `code_id` in any spec is absent from this registry.

Derivation rules (normative):
- `subsystem` in `ErrorRecord` is derived from registry `category` for `code_id` with exact bytewise equality.
- `privacy_class` default is `INTERNAL` for all registry codes unless overridden below:
  - `ATTESTATION_FAILURE` -> `CONFIDENTIAL`
  - `PRIVACY_BUDGET_EXCEEDED` -> `CONFIDENTIAL`
  - `ACCOUNTANT_OVERFLOW` -> `CONFIDENTIAL`
  - `ACCOUNTANT_DIVERGENCE` -> `CONFIDENTIAL`
  - `TRACE_CAP_EXCEEDED_MANDATORY` -> `INTERNAL`
- `deterministic_fields_required` keys must be present exactly by key name either as top-level `ErrorRecord` fields or as keys in `diagnostics`.
- Canonical field name is `failure_operator`; `operator_id` is forbidden in new records and accepted only as deprecated input alias for backward-compat validation.

### II.G ErrorRecord Schema (Normative)
- Required fields:
  - `code_id:string`
  - `numeric_code:uint32`
  - `severity:enum("FATAL","ERROR","WARN")`
  - `subsystem:enum("config","data","model","tmmu","dp","trace","backend","security","distributed","runtime","replay")`
  - `t:uint64`
  - `rank:uint32`
  - `failure_operator:string`
  - `replay_token:bytes32`
  - `message:string`
  - `retryable:bool`
  - `privacy_class:enum("PUBLIC","INTERNAL","CONFIDENTIAL")`
- Optional fields:
  - `diagnostics:map<string, scalar|string|bytes>` with deterministic key ordering and size cap.

---
## 3) Initialization
1. Load registry.
2. Validate uniqueness and payload schemas.
3. Initialize counters.

---
## 4) Operator Manifest
- `Glyphser.Error.Emit`
- `Glyphser.Error.ValidateRecord`
- `Glyphser.Error.SerializeRecord`

---
## 5) Operator Definitions

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `Glyphser.Error.Emit`  
**Category:** Error  
**Signature:** `(code, context -> error_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** emits standardized failure record.

**Operator:** `Glyphser.Error.ValidateRecord`  
**Category:** Error  
**Signature:** `(error_record -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks required fields and payload schema, then enforces per-`code_id` deterministic field requirements from registry.
**Validation requirements:**
- `code_id` MUST exist in registry and `numeric_code`/`severity`/`retryable` MUST match registry.
- `subsystem` MUST equal derived subsystem from registry `category`.
- `privacy_class` MUST equal derived privacy class from derivation rules above.
- For each key in `deterministic_fields_required` for `code_id`, key MUST exist either:
  - as top-level field of `ErrorRecord`, or
  - in `diagnostics` under exactly the same key name.
- Deprecated alias handling: if `diagnostics.operator_id` is present and `failure_operator` missing for backward compatibility inputs, validator MAY map alias only for legacy ingest then MUST emit canonical `failure_operator` on serialization.

**Operator:** `Glyphser.Error.SerializeRecord`  
**Category:** Error  
**Signature:** `(error_record -> bytes)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical encoding for trace/certificate inclusion.

---
## 6) Procedure
```text
1. Emit(code, context)
2. ValidateRecord (global schema + per-code required fields)
3. SerializeRecord
4. Return record + bytes
```

---
## 7) Trace & Metrics
### Logging rule
All failures must log one canonical record.
### Trace schema
- `run_header`: registry_version
- `iter`: error_code, operator, t, replay_token
- `run_end`: failure summary
### Metric schema
- `error_code_frequency`, `first_failure_t`
### Comparability guarantee
Comparable iff registry and serialization rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Ensures code uniqueness, schema completeness, deterministic serialization.
#### VII.B Operator test vectors (mandatory)
Known contexts map to exact error records.
#### VII.C Golden traces (mandatory)
Golden serialized error bytes for canonical contexts.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for emitted record and serialization.
#### VIII.B Allowed refactor categories
- internal formatting optimizations preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
Exact record and byte-level comparison.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- registry snapshot and counters.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- identical future error records for same contexts.
