# Glyphser Redaction Policy Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Security.RedactionPolicy`
**Purpose (1 sentence):** Define deterministic field-level redaction rules that preserve verifiability while preventing sensitive leakage.
**Spec Version:** `Glyphser.Security.RedactionPolicy` | 2026-02-20 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Deterministic privacy-preserving telemetry transformation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Security.RedactionPolicy`
- **Purpose:** Deterministic redaction contract for trace and governance records.

### 0.A Objective Semantics
- This contract performs deterministic policy validation and deterministic record transformation.
- Primary objective: eliminate raw sensitive payload exposure while preserving replay/audit comparability.

### 0.B Reproducibility Contract
- Replayable given `(record_blob, schema_version, redaction_mode, redaction_policy_hash, redaction_key_id, preimage_format_id)`.
- `record_blob` MUST be canonical CBOR encoded.
- Canonical CBOR profile is RFC 8949 Section 4.2.1 (Core Deterministic Encoding Requirements), with additional constraints:
  - Floating-point values MUST be encoded as IEEE 754 binary64.
  - Map keys MUST be sorted by bytewise lexicographic order of canonical key encodings.
- Policy object is loaded by `redaction_policy_hash`.

### 0.C Numeric Policy
- This section also defines deterministic transform-selection policy.
- Effective transform decision is deterministic:
  1. If `field_transform_map` has path entry, use that transform.
  2. Else if classification is `CONFIDENTIAL`, use input `redaction_mode`.
  3. Else use `NONE`.
- `BUCKET_V1` is allowed only for numeric fields.
- For `CONFIDENTIAL` fields, effective transform MUST be `HMAC_SHA256_V1` or `BUCKET_V1`; `NONE` is invalid.

### 0.D Ordering and Tie-Break Policy
- Canonical field path is a CBOR array path (`FieldPath`) of UTF-8 string keys and non-negative uint array indices.
- Canonical traversal order is bytewise lexicographic order of canonical CBOR bytes of `FieldPath`.
- All audit/path sorting MUST use this same ordering.

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel redaction is allowed only if final output is reassembled by canonical path ordering.
- Deterministic merge: gather `(path, value, audit_entry)` triples, then sort by canonical path bytes before emit.

### 0.F Environment and Dependency Policy
- HMAC implementation version and key policy are committed by `redaction_policy_hash`.
- `redaction_key_id` must map to stable key bits for replay windows.

### 0.G Operator Manifest
- `Glyphser.Security.RedactRecord`
- `Glyphser.Security.ComputeRedactionPolicyHash`
- `Glyphser.Security.ValidateRedactionCoverage`
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- `Glyphser.Security.*` namespace.

### 0.I Outputs and Metric Schema
- Outputs: `(redacted_record, redaction_audit)`.
- `redacted_record` MUST be encoded as canonical CBOR using the same profile defined in Section 0.B.
- Validation output schema:
  - `coverage_report = { valid: bool, errors: array<tstr> }` (canonical CBOR map).
- `redaction_audit` schema:
  - `record_id:tstr` (extracted from original input at top-level path `["record_id"]` before redaction; if absent or non-text, use `""`)
  - `policy_hash:bytes32`
  - `redaction_key_id:tstr`
  - `redacted_fields:array<AuditEntry>` sorted by canonical path order
  - `redacted_field_count:uint64`
  - `forbidden_raw_field_count:uint64`
- `AuditEntry`:
  - `path:FieldPath`
  - `transform:enum("NONE","HMAC_SHA256_V1","BUCKET_V1")`
  - `classification:enum("PUBLIC","INTERNAL","CONFIDENTIAL")`
- `forbidden_raw_field_count` = count of redactable fields found untransformed in output; MUST be `0` on success.
- A field is redactable iff its effective transform (Section 0.C) is not `NONE`.

### 0.J Spec Lifecycle Governance
- Any change in field-path representation, transform semantics, preimage format, or bucketization is MAJOR.

### 0.K Failure and Error Semantics
- On fatal error, `RedactRecord` MUST NOT return outputs.
- It MUST emit deterministic `CONTRACT_VIOLATION` via `Glyphser.Error.Emit` with reason code.
- Fatal reasons include:
  - `POLICY_NOT_FOUND`
  - `KEY_NOT_FOUND`
  - `KEY_EXPIRED`
  - `SCHEMA_MISMATCH`
  - `MANDATORY_FIELD_MISSING`
  - `MANDATORY_FIELD_REDACTED`
  - `INVALID_BUCKET_RULES`
  - `INVALID_PATH_IN_POLICY`
  - `TRANSFORM_TYPE_MISMATCH`
  - `KEY_NOT_AUTHORIZED`
  - `BUCKET_VALUE_NAN`
  - `NULL_VALUE_FOR_BUCKET`
  - `INVALID_PREIMAGE_FORMAT`
  - `INVALID_REDACTION_MODE`
  - `SCHEMA_NOT_FOUND`
  - `INVALID_CBOR`
  - `INVALID_TRANSFORM_VALUE`
  - `INVALID_VALUE_TYPE`

### 0.L Input/Data Provenance
- Source schema hash and schema version are mandatory redaction inputs.

---
### 0.Z EQC Mandatory Declarations Addendum
- No stochastic operators in v1.
- Determinism level: `BITWISE` for `redacted_record` and `redaction_audit`.
- NaN/Inf policy for bucketization values:
  - NaN => abort (`BUCKET_VALUE_NAN`).
  - ±Inf => clamp to boundary bucket as defined below.

## 2) System Model
### I.A Persistent State
- `redaction_policy_registry`
- key metadata registry with `not_before` / `not_after` validity window (both integer Unix epoch seconds, UTC)
- schema registry keyed by `schema_version`

### I.B Inputs and Hyperparameters
- `record_blob` (canonical CBOR map/object)
- `schema_version:tstr` (CBOR text string)
- `redaction_mode:enum("NONE","HMAC_SHA256_V1","BUCKET_V1")`
- `redaction_key_id:tstr`
- `redaction_policy_hash:bytes32`

### I.C Constraints and Feasible Set
- Policy paths must exist in schema.
- All map keys in records subject to this policy MUST be CBOR text strings.
- Mandatory verification fields must exist in record and remain unredacted.
- Composite and leaf handling must follow Section II.G.

### I.D Transient Variables
- canonical field paths
- canonical preimages
- transformed values
- coverage diagnostics

### I.E Invariants and Assertions
- No raw confidential payload in successful output.
- Mandatory verification fields present and unredacted.

### II.F Policy and Classification Schema (Normative)
Classifications:
- `PUBLIC`
- `INTERNAL`
- `CONFIDENTIAL`

Policy object (loaded by `redaction_policy_hash`) must contain:
- `policy_rules:map` (reserved in v1; implementations MUST ignore entries for forward compatibility)
- `field_classification_map:map<FieldPath, classification>`
- `field_transform_map:map<FieldPath, transform>` (optional overrides)
- `preimage_format_id:tstr` (v1 requires `redaction`)
- `key_policy:map` with:
  - `allowed_key_ids:array<tstr>`
  - v1 implementations MUST ignore unknown `key_policy` fields for forward compatibility.
- `bucket_rules:map<FieldPath, array<float64>>`

### II.G Canonical Redaction Rules (Normative)
Transforms:
- `NONE`
- `HMAC_SHA256_V1`
- `BUCKET_V1`

Leaf/composite rules:
- Leaf = primitive schema type (`null`, `bool`, `number`, `string`, `bytes`).
- Composite = map/array.
- Default behavior: traverse composites recursively to leaves.
- If a composite path has explicit transform override/classification requiring transform, transform the whole composite value as one unit and skip descendants.

Field path (`FieldPath`):
- CBOR array with string keys and uint indices only.
- Map keys in paths are always strings.

Canonical field value:
- `field_value_canonical` is canonical CBOR bytes of value.
- For composite transformed as whole, use canonical CBOR of entire composite.
- For floats, encode as CBOR float64.
- Canonical CBOR reference: RFC 8949 deterministic encoding + project Canonical-CBOR profile.

HMAC preimage:
- `CBOR_CANONICAL(["redaction", [schema_version, field_path, field_value_canonical]])`.
- HMAC output MUST be encoded in output record as CBOR byte string length 32.

Bucketization (`BUCKET_V1`):
- `bucket_rules[path] = [b0, b1, ..., bn]`, finite binary64, strictly increasing, `n>=1`.
- At least two boundaries required.
- Selection for numeric `x`:
  - Interpret `x` as the exact mathematical real number represented by canonical CBOR value encoding (independent of whether source numeric is integer or float).
  - Comparisons are exact real-number comparisons (no tolerance, no implementation-defined rounding).
  - if `x < b0` => bucket `0`.
  - for `i=0..n-2`: if `b_i <= x < b_{i+1}` => bucket `i`.
  - if `x >= b_n` => bucket `n-1`.
- Boundary comparisons are exact.
- NaN is invalid (abort with `BUCKET_VALUE_NAN`).
- Null is invalid for `BUCKET_V1` (abort with `NULL_VALUE_FOR_BUCKET`).
- Output representation: `"bucket_<index>"`, where `<index>` is decimal integer without leading zeros.
- Policy conflict rule: reject any ancestor/descendant overlap among effective transforms.
  - Let effective transform be resolved per Section 0.C.
  - For any two distinct paths `p` and `q` where one is a proper prefix of the other, it is invalid if both effective transforms are not `NONE`.
  - Such policy/configuration MUST be rejected.

### II.H Mandatory Unredacted Verification Fields
These fields are mandatory at top-level paths and must remain unredacted:
- `["record_id"]`
- `["replay_token"]`
- `["record_hash"]`
- `["trace_final_hash"]`
- `["policy_bundle_hash"]`
- `["authz_decision_hash"]`
- `["policy_gate_hash"]`
- `["checkpoint_hash"]`
- `["execution_certificate_hash"]`

### II.I Policy Hash Definition
- `redaction_policy_hash = SHA-256(CBOR_CANONICAL(["redaction_policy", [policy_rules, field_classification_map, field_transform_map, preimage_format_id, key_policy, bucket_rules]]))`.

---
## 3) Initialization
1. Load schema from schema registry by `schema_version`.
2. Load policy by `redaction_policy_hash`.
3. Load key metadata by `redaction_key_id`; verify time window using Unix epoch seconds (UTC) integer comparison.
4. Verify `preimage_format_id == "redaction"`; else abort with `INVALID_PREIMAGE_FORMAT`.
5. Verify `redaction_key_id` is in `key_policy.allowed_key_ids`; else abort with `KEY_NOT_AUTHORIZED`.
6. Run `ValidateRedactionCoverage`; abort on failure.

---
## 4) Operator Manifest
- `Glyphser.Security.RedactRecord`
- `Glyphser.Security.ComputeRedactionPolicyHash`
- `Glyphser.Security.ValidateRedactionCoverage`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
External operator reference: `Glyphser.Error.Emit` is defined in `docs/layer1-foundation/Error-Codes.md`.

**Operator:** `Glyphser.Security.RedactRecord`
- **Category:** Security
- **Signature:** `(record_blob, schema_version, redaction_mode, redaction_key_id, redaction_policy_hash -> redacted_record, redaction_audit)`
- **Purity class:** IO
- **Determinism:** deterministic
- **Definition:**
  - Validates `redaction_mode` is one of `NONE | HMAC_SHA256_V1 | BUCKET_V1`; else abort with `INVALID_REDACTION_MODE`.
  - Resolves schema by `schema_version`; if missing, abort with `SCHEMA_NOT_FOUND`.
  - Decodes canonical CBOR record; if malformed or non-canonical, abort with `INVALID_CBOR`.
  - Traverses canonical paths and applies deterministic transform decision logic from 0.C.
  - For effective transform `BUCKET_V1`, runtime value at path MUST be numeric (CBOR int or float); otherwise abort with `INVALID_VALUE_TYPE`.
  - Missing optional fields are skipped and not audited in v1.
  - Missing mandatory fields cause abort.
  - Output record preserves exact input path presence/absence; only transformed field values differ.

**Operator:** `Glyphser.Security.ComputeRedactionPolicyHash`
- **Category:** Security
- **Signature:** `(policy_rules, field_classification_map, field_transform_map, preimage_format_id, key_policy, bucket_rules -> redaction_policy_hash)`
- **Purity class:** PURE
- **Determinism:** deterministic
- **Definition:** Computes hash exactly per Section II.I.

**Operator:** `Glyphser.Security.ValidateRedactionCoverage`
- **Category:** Security
- **Signature:** `(record_schema, redaction_policy_hash -> coverage_report)`
- **Purity class:** PURE
- **Determinism:** deterministic
- **Definition:**
  - Validates all policy-map keys are well-formed `FieldPath` values (CBOR array elements must be string key or uint index).
  - Validates all `field_transform_map` values are in allowed transform enum: `NONE | HMAC_SHA256_V1 | BUCKET_V1`.
  - Validates all policy paths exist in schema.
  - Validates transform-type compatibility (`BUCKET_V1` numeric only).
  - Validates mandatory fields non-redactable and present in schema.
  - Validates no mandatory field has transformed ancestor path (no proper-prefix path with effective transform != `NONE`).
  - Validates bucket boundaries finite/strictly increasing/min-length.
  - Validates each `CONFIDENTIAL` field effective transform is `HMAC_SHA256_V1` or `BUCKET_V1` (not `NONE`).
  - Validates bucket-rules completeness:
    - every effective `BUCKET_V1` field has corresponding `bucket_rules` entry,
    - every `bucket_rules` entry corresponds to effective `BUCKET_V1`.
  - Validates effective-transform ancestor/descendant conflict rule (no proper-prefix pair with both effective transforms != `NONE`).
  - All `errors` entries MUST be fatal reason codes defined in Section 0.K.
  - If multiple errors are detected, `errors` MUST be sorted lexicographically by code string.
  - Returns `coverage_report = { valid: bool, errors: array<tstr> }`; on success `valid=true` and `errors=[]`.

---
## 6) Procedure
1. Resolve schema by `schema_version` and policy by `redaction_policy_hash`; if schema missing, abort with `SCHEMA_NOT_FOUND`.
2. Validate key presence, validity window, and key authorization (`redaction_key_id in key_policy.allowed_key_ids`).
3. Validate `preimage_format_id == "redaction"`.
4. Run `ValidateRedactionCoverage`.
5. If `coverage_report.valid == false`, abort with first error in lexicographically sorted `coverage_report.errors`.
6. Transform record deterministically in canonical path order (or parallel with deterministic merge).
7. Assert mandatory fields present and unredacted.
8. Emit canonical `redaction_audit`.
9. Return `redacted_record`.

---
## 7) Trace & Metrics
### Logging rule
- Redaction decisions emit deterministic audit records without raw confidential payload values.

### Trace schema
- `run_header`: `redaction_mode`, `redaction_key_id`, `redaction_policy_hash`
- `iter`: `record_id`, `field_path:FieldPath` (canonical CBOR array path encoding), `transform`, `status`
- `run_end`: `coverage_status`, `redacted_field_count`, `forbidden_raw_field_count`

### Metric schema
- `redacted_field_count`
- `forbidden_raw_field_count`

### Comparability guarantee
- Comparable iff `redaction_policy_hash`, `redaction_mode`, `redaction_key_id`, `preimage_format_id`, and canonicalization policy are identical.

---
## 8) Validation
### VII.A Lint rules (mandatory)
- No undeclared transforms.
- No raw confidential fields in outputs.
- Field-path format and canonical traversal order compliance.
- Mandatory verification fields must be top-level and non-redactable.
- Reject policy paths absent from schema.
- Reject invalid bucket rules (non-finite, non-increasing, length < 2).
- Reject effective-transform prefix conflicts (no ancestor/descendant path pair may both have effective transforms != `NONE`).

### VII.B Operator test vectors (mandatory)
- HMAC preimage vectors.
- Bucket vectors including equality-to-boundary and out-of-range cases.
- Missing/expired-key failures.

### VII.C Golden traces (mandatory)
- Golden success traces and deterministic failure traces (with error reason codes).

---
## 9) Refactor & Equivalence
### VIII.A Equivalence levels
- `E0` for transformed outputs and audit hashes.

### VIII.B Allowed refactor categories
- Runtime optimizations preserving byte-identical outputs.

### VIII.C Equivalence test procedure (mandatory)
- Exact compare of `redacted_record` and `redaction_audit` hashes.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- `redaction_policy_hash`
- `redaction_key_id`
- `stream_cursor:uint64` (last fully processed record index in batch stream; single-record mode uses `0`)

### Serialization
- Canonical CBOR.

### Restore semantics
- Restore requires same policy hash and key id availability/immutability within replay window.
- For identical inputs and cursor state, restored run must produce identical outputs.
