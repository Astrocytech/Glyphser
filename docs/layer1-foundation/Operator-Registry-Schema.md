# Glyphser Operator Registry Schema Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Registry.OperatorRegistrySchema`  
**Purpose (1 sentence):** Define the authoritative machine-readable schema for `contracts/operator_registry.cbor` and its deterministic validation rules.  
**Spec Version:** `Glyphser.Registry.OperatorRegistrySchema` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Interface governance and contract integrity.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Registry.OperatorRegistrySchema`
- **Purpose (1 sentence):** Canonical operator registry schema and validation.
### 0.A Objective Semantics
- This is a schema/registry integrity contract (not an optimization objective).
- Primary comparison rule: deterministic schema validity and digest equality.
- Invalid objective policy: schema violations are deterministic failures.
### 0.B Reproducibility Contract
- Replayable given `(registry_schema_version, canonical_cbor_bytes, digest_catalog_blob, error_codes_blob, capability_catalog_blob, schema_catalog_blob, expected_catalog_hashes)`.
- Hash/token paths use `SHA-256(CBOR_CANONICAL(...))`.
 - `CBOR_CANONICAL` is normative as defined in `docs/layer1-foundation/Canonical-CBOR-Profile.md`.
### 0.C Numeric Policy
- Integer fields are unsigned fixed ranges.
- Resolved digest values are `bytes32`; `digest_ref` fields are textual references resolved deterministically to `bytes32`.
### 0.D Ordering and Tie-Break Policy
- Registry records sorted by `(operator_id, version_num)` where:
  - `operator_id` comparison is bytewise UTF-8 lexicographic, case-sensitive, locale-independent.
  - `version_num = parse_uint(version[1:])` from `version` format `^v[0-9]+$`, compared numerically (not lexicographically).
### 0.E Parallel, Concurrency, and Reduction Policy
- Validation can be parallelized but merged in deterministic key order.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for validation reports and computed hashes.
### 0.G Operator Manifest
- `Glyphser.Registry.ValidateOperatorRegistry`
- `Glyphser.Registry.ComputeRegistryHash`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Registry file path: `contracts/operator_registry.cbor`.
- Registry file MUST be stored in canonical CBOR form as defined by `CBOR_CANONICAL` (not only logically decodable to canonical form).
### 0.I Outputs and Metric Schema
- Outputs: `(validation_report, operator_registry_root_hash)`.
- Metrics: `operators_count`, `schema_errors`.
- `operator_registry_root_hash` output encoding: raw `bytes32` (hex/base64 are presentation-only views).
- `validation_report` is emitted as a canonical CBOR map and includes the metrics fields.
### 0.J Spec Lifecycle Governance
- Required field changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort-only with deterministic failure record.
- Validation failures MUST map to deterministic `code_id` values as defined in §5 `validation_report` schema.
- These `code_id` values MUST map to authoritative error catalog entries in `docs/layer1-foundation/Error-Codes.md`.
### 0.L Input/Data Provenance
- Input registry blob must be content-addressed and immutable.
- All input catalog blobs (`digest_catalog_blob`, `error_codes_blob`, `capability_catalog_blob`, `schema_catalog_blob`) MUST be canonical CBOR.

---
## 2) System Model
### I.A Persistent State
- `registry_schema`.
### I.B Inputs and Hyperparameters
- `operator_registry_blob`.
- `digest_catalog_blob` (canonical CBOR; schema per `docs/layer1-foundation/Digest-Catalog.md`)
- `error_codes_blob` (canonical CBOR; schema per `docs/layer1-foundation/Error-Codes.md`)
- `capability_catalog_blob` (canonical CBOR; schema per `docs/layer2-specs/Security-Compliance-Profile.md`)
- `schema_catalog_blob` (canonical CBOR; schema-artifact index catalog)
- `expected_catalog_hashes:map<string,bytes32>` (canonical CBOR map with keys `digest_catalog`, `error_codes_catalog`, `capability_catalog`, `schema_catalog`; empty map means no expected-hash comparison)
  - unknown keys in `expected_catalog_hashes` MUST be ignored and MUST NOT affect validation results.
### I.C Constraints and Feasible Set
- Valid iff all required keys/types/enum values pass.
### I.D Transient Variables
- decoded records and diagnostics.
### I.E Invariants and Assertions
- unique `(operator_id, version)` keys.

### II.E DigestRef and Canonical Text Rules (Normative)
- `digest_ref` textual grammar:
  - inline digest: `sha256:<hex64>`
  - catalog label: `sha256:<label>`
- Disambiguation:
  - if `<tail>` matches `^[0-9a-fA-F]{64}$`, treat as inline digest and normalize to lowercase before parsing.
  - otherwise treat as catalog label and resolve using the provided `digest_catalog_blob` (whose schema is defined in `docs/layer1-foundation/Digest-Catalog.md`).
- Resolution output:
  - resolved digest is always `bytes32`.
  - resolution cycles are invalid and MUST fail deterministically with `DIGEST_RESOLUTION_FAILURE`.
- Text constraints (all string fields in operator records):
  - strings MUST be valid UTF-8.
  - fields requiring NFC validity (including `operator_id`, `version`, `method`, `required_capabilities[*]`, `owner_team`, `replacement_operator_id`) MUST already be NFC-normalized; non-NFC values MUST be rejected deterministically during validation.
  - comparisons are bytewise UTF-8, case-sensitive, locale-independent.
  - `operator_id`, `version`, `method`, and `required_capabilities[*]` MUST match `^[A-Za-z0-9_\\-\\.]{1,128}$`.

### II.F Canonical Operator Record Schema (Normative)
- Top-level registry object schema:
  - `registry_schema_version:uint32`
  - `operator_records:array<operator_record>`
  - for this contract version, `registry_schema_version` MUST equal `1`.
  - `operator_records` MUST be stored in-file already sorted by `0.D` ordering (unique canonical file representation for content addressing).
- `side_effect_enum` allowed values:
  - `ADVANCES_RNG`, `ADVANCES_CURSOR`, `MUTATES_ACCOUNTANT`, `MUTATES_MODEL_STATE`, `PERFORMS_IO`, `NETWORK_COMM`, `ALLOCATES_MEMORY`.
- Required fields per operator record:
  - `operator_id:string`
  - `version:string` (normalized format `v<nonnegative-integer>`, regex `^v[0-9]+$`)
  - `method:string`
  - `surface:enum("SYSCALL","SERVICE")`
  - `request_schema_digest:digest_ref`
  - `response_schema_digest:digest_ref`
  - `signature_digest:bytes32`
  - `side_effects:array<side_effect_enum>` (sorted, unique by bytewise UTF-8 enum-id string order; allowed values listed above)
  - `allowed_error_codes:array<error_code_id>` where `error_code_id:string` and value MUST exist in the provided `error_codes_blob` (whose schema is defined in `docs/layer1-foundation/Error-Codes.md`) (sorted, unique by bytewise UTF-8 code-id order)
  - `purity_class:enum("PURE","STATEFUL","IO")`
  - `required_capabilities:array<string>` (sorted, unique by bytewise UTF-8 lexicographic order; each capability id matches `^CAP_[A-Z0-9_]{1,64}$`)
  - `idempotent:bool`
  - `rng_usage:enum("NONE","PHILOX4x32_10")`
  - `determinism_class:enum("DETERMINISTIC","STOCHASTIC","MIXED")`
- Optional fields:
  - `owner_team:string`
  - `deprecated:bool`
  - `replacement_operator_id:string`
- Optional field constraints:
  - `owner_team`, when present, MUST match `^[A-Za-z0-9_\\-\\.]{1,128}$`.
  - if `deprecated=true`, `replacement_operator_id` SHOULD be present.
  - if `replacement_operator_id` is present, it MUST resolve to an existing `operator_id` in the same registry.
  - `replacement_operator_id`, when present, MUST match `^[A-Za-z0-9_\\-\\.]{1,128}$`.
- Enum CBOR representation rule (all enum-typed fields in this section):
  - enum values MUST be encoded as UTF-8 text strings equal to their symbol ids.
- Capability validation rule:
  - each `required_capabilities` entry MUST exist in the provided `capability_catalog_blob` (whose schema is defined in `docs/layer2-specs/Security-Compliance-Profile.md`).
- Method/surface compatibility rules:
  - if `surface="SYSCALL"`, `method` MUST be one of `CALL|INTERNAL`.
  - if `surface="SERVICE"`, `method` MUST be one of `HTTP|GRPC|CALL`.
- Optional-field encoding rule:
  - missing optional fields MUST be omitted from canonical CBOR (no implicit defaults and no implicit null insertion).
- Purity/determinism compatibility rule:
  - `purity_class="PURE"` with `determinism_class="STOCHASTIC"` is invalid unless `rng_usage != "NONE"`.
- Unknown-field policy:
  - operator records MUST NOT contain fields outside required+optional sets above.
  - top-level registry object MUST NOT contain unknown fields.
  - presence of unknown fields MUST emit `UNKNOWN_FIELD`.
- Canonical CBOR enforcement:
  - indefinite-length arrays/maps/strings are forbidden.
  - map keys must follow canonical sorting rules from `Canonical-CBOR-Profile.md`.

### II.G Registry Hash (Normative)
- Canonical operator list is `operator_records` in the ordering defined by `0.D`.
- `operator_registry_root_hash = SHA-256(CBOR_CANONICAL(["operator_registry", [registry_schema_version, operator_records]]))`.
- `registry_hash` is an exact alias of `operator_registry_root_hash` for backward compatibility.
- Version/tag consistency check:
  - the numeric suffix in domain tag `operator_registry_vN` used for hash preimage MUST equal top-level `registry_schema_version`.

### II.H SignatureDigest Rule (Normative, Global)
- Signature digest computation is defined only here and consumed by all interface/mapping/backend docs.
- Preimage:
  - `signature_digest = SHA-256(CBOR_CANONICAL(["sig", [operator_id, version, method, request_schema_digest_resolved, response_schema_digest_resolved, sorted(side_effects), sorted(allowed_error_codes)]]))`.
- Sorting semantics for preimage arrays:
  - `sorted(side_effects)` and `sorted(allowed_error_codes)` use the same bytewise UTF-8 lexicographic order defined in `0.D`.
- `request_schema_digest_resolved` and `response_schema_digest_resolved` are resolved bytes32 values after `digest_ref` resolution.
- If any `digest_ref` fails resolution, validation MUST fail deterministically with `DIGEST_RESOLUTION_FAILURE`; no placeholder or partial signature digest is permitted.
- `signature_digest` correctness check is mandatory:
  - each operator record’s stored `signature_digest` MUST equal the recomputed preimage hash from this section.
- Referenced-schema existence check:
  - resolved request/response schema digests MUST resolve to known schema artifacts in the provided `schema_catalog_blob`; unresolved references MUST emit `DIGEST_RESOLUTION_FAILURE`.
- Any mismatch with this rule during validation MUST emit a deterministic code from §5 (`DIGEST_RESOLUTION_FAILURE` or `SIGNATURE_MISMATCH`, as applicable).

### II.I Operator Registry Root Commitment (Normative)
- Authoritative commitment is `operator_registry_root_hash` from `II.G`.
- `operator_registry_root_hash` is the required value bound as `operator_contracts_root_hash` in execution certificates and checkpoint headers.
- Version-evolution rule:
  - MAJOR schema/version change MUST update domain tag prefix in `II.G` (for example `operator_registry`).
- External catalog pinning rule:
  - validation MUST compute catalog hashes from provided catalog blobs and include them in `validation_report`.
- `digest_catalog_hash`, `error_codes_catalog_hash`, `capability_catalog_hash`, and `schema_catalog_hash` are computed as `SHA-256` of the corresponding canonical CBOR input blob bytes.
  - caller-side trust verification compares reported catalog hashes against expected trusted hashes.
  - validator MUST compare computed hashes against `expected_catalog_hashes` when the corresponding expected key is present, and MUST emit `CATALOG_HASH_MISMATCH` on mismatch.

---
## 3) Initialization
1. Load `contracts/operator_registry.cbor`.
2. Decode canonical CBOR.
3. If CBOR decoding fails or canonical-form checks fail, emit deterministic `MALFORMED_CBOR` and abort.
4. Initialize validation diagnostics.

---
## 4) Operator Manifest
- `Glyphser.Registry.ValidateOperatorRegistry`
- `Glyphser.Registry.ComputeRegistryHash`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Registry.ValidateOperatorRegistry`  
**Category:** Governance  
**Signature:** `(registry_blob, digest_catalog_blob, error_codes_blob, capability_catalog_blob, schema_catalog_blob, expected_catalog_hashes -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates required fields, enum values, key uniqueness, sorted list invariants, method/surface compatibility, digest_ref resolution, per-record signature_digest correctness, existence of `allowed_error_codes` in error catalog, existence of `required_capabilities` in capability catalog, validity of `replacement_operator_id` references, schema version/tag consistency, and existence of resolved request/response schema digests in schema catalog.
**validation_report minimum schema (canonical CBOR map):**
  - `is_valid:bool`
  - `root_hash?:bytes32` (present when valid)
  - `operators_count:uint64`
  - `schema_errors:uint64`
  - `digest_catalog_hash:bytes32`
  - `error_codes_catalog_hash:bytes32`
  - `capability_catalog_hash:bytes32`
  - `schema_catalog_hash:bytes32`
  - `errors:array<{code_id:enum("MALFORMED_CBOR","MISSING_REQUIRED_FIELD","UNKNOWN_FIELD","INVALID_FIELD_TYPE","DIGEST_RESOLUTION_FAILURE","SIGNATURE_MISMATCH","INVALID_ENUM_VALUE","INVALID_SORT_ORDER","DUPLICATE_VALUE","INVALID_METHOD_FOR_SURFACE","INVALID_PURITY_DETERMINISM_COMBINATION","UNKNOWN_CAPABILITY","UNKNOWN_ERROR_CODE","INVALID_OPERATOR_REFERENCE","SCHEMA_VERSION_MISMATCH","CATALOG_HASH_MISMATCH","CATALOG_PARSE_ERROR"), path:string}>`
  - `path` format is RFC 6901 JSON Pointer over a virtual root object with keys:
    - `/registry` for registry object paths (e.g., `/registry/operator_records/3/method`)
    - `/digest_catalog`, `/error_codes_catalog`, `/capability_catalog`, `/schema_catalog` for catalog-level failures
  - deeper catalog paths are allowed (for example `/digest_catalog/entries/5`) using catalog-local schema structure.
  - `CATALOG_HASH_MISMATCH` path MUST be the corresponding catalog root path (`/digest_catalog`, `/error_codes_catalog`, `/capability_catalog`, or `/schema_catalog`).
  - error ordering is deterministic by bytewise UTF-8 lexicographic `(path, code_id)`.

**Operator:** `Glyphser.Registry.ComputeRegistryHash`  
**Category:** Governance  
**Signature:** `(validated_registry -> operator_registry_root_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes `operator_registry_root_hash = SHA-256(CBOR_CANONICAL(["operator_registry", [registry_schema_version, operator_records]]))` using canonical serialization profile `CanonicalSerialization` from `docs/layer1-foundation/Canonical-CBOR-Profile.md`, where `operator_records` are ordered by `(operator_id, version_num)` and `version_num = parse_uint(version[1:])`.

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

---
## 6) Procedure
```text
1. ValidateOperatorRegistry (with explicit catalog blobs and expected_catalog_hashes; derive/pin catalog hashes)
2. ComputeRegistryHash
3. Return report + operator_registry_root_hash
```

---
## 7) Trace & Metrics
### Logging rule
- Validation emits deterministic registry diagnostics.
### Trace schema
- `run_header`: `registry_schema_version:uint32`
- `iter`: array of pairs `[operator_id:string, status:enum(valid|invalid)]` in registry order
- `run_end`: `operator_registry_root_hash:bytes32`
### Trace encoding (normative)
- trace output MUST be canonical CBOR map with fixed keys:
  - `{ "run_header": uint, "iter": [ [tstr, tstr], ... ], "run_end": bytes }`
### Trace status enum
- `status` MUST be one of: `valid`, `invalid`.
### Metric schema
- `operators_count`, `schema_errors`
### Comparability guarantee
- Comparable iff schema version and canonical hash rule are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- all required fields present and typed.
- digest_ref resolution must succeed for all digest_ref fields.
- optional fields must be omitted when absent (no implicit default/null materialization).
- `signature_digest` must match recomputation for every record.
- `side_effects`, `allowed_error_codes`, `required_capabilities` must be present even when empty (encoded as empty arrays).
- empty `side_effects` array is the only valid representation of “no side effects” (no `NONE` enum token).
- sorted arrays must also be duplicate-free; duplicates MUST emit `DUPLICATE_VALUE`.
- method/surface mismatch MUST emit `INVALID_METHOD_FOR_SURFACE`.
- purity/determinism incompatibility MUST emit `INVALID_PURITY_DETERMINISM_COMBINATION`.
- unknown capability MUST emit `UNKNOWN_CAPABILITY`.
- unknown allowed error code MUST emit `UNKNOWN_ERROR_CODE`.
- missing/invalid replacement operator reference MUST emit `INVALID_OPERATOR_REFERENCE`.
- registry version vs hash-tag suffix mismatch MUST emit `SCHEMA_VERSION_MISMATCH` at path `/registry/registry_schema_version`.
- expected-vs-derived catalog hash mismatch MUST emit `CATALOG_HASH_MISMATCH` at the corresponding catalog root path.
- if any catalog blob fails canonical-CBOR decoding/parsing, validator MUST emit `CATALOG_PARSE_ERROR` at the corresponding catalog root path.
#### VII.B Operator test vectors (mandatory)
- valid/invalid registry fixtures.
#### VII.C Golden traces (mandatory)
- golden registry hash snapshots.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for validation report and registry hash.
#### VIII.B Allowed refactor categories
- parser/runtime implementation changes preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of report and registry hash.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- `last_validated_registry_hash:bytes32` (present only if validation completed successfully).
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- Validation is a pure function; checkpoints store final results only.
- Intermediate resume is not supported; interrupted validation MUST be rerun from the beginning.

---
## 11) Strict-Ingest-by-Default Policy (Normative)
- All ingest paths (SDKs, services, CI tooling, registry publishers) MUST run strict validation mode by default:
  - reject unknown fields,
  - reject non-canonical ordering,
  - reject duplicate entries in sorted arrays,
  - reject digest/signature mismatches.
- Compatibility shims MAY exist only behind explicit opt-in flags and MUST emit warnings with migration deadlines.
