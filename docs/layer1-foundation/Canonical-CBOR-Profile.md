# Glyphser Canonical CBOR Profile Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Serialization.CanonicalCBORProfile`  
**Purpose (1 sentence):** Define the single canonical CBOR encoding profile used for all commitment hashes and signatures.  
**Spec Version:** `Glyphser.Serialization.CanonicalCBORProfile` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Deterministic serialization and cryptographic commitment consistency.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Serialization.CanonicalCBORProfile`
- **Purpose (1 sentence):** Single-source canonical CBOR profile.
### 0.A Objective Semantics
- Primary comparison rule: byte-identical canonical encoding.
- Invalid objective policy: non-canonical payload is invalid.
### 0.B Reproducibility Contract
- Replayable given `(profile_version, input_object)`.
### 0.C Numeric Policy
- All floating-point values MUST encode as IEEE-754 binary64.
- Floating-point inputs MUST already be IEEE-754 binary64 values; encoder preserves exact input bit patterns subject to canonical special-value constraints in II.F.
- No conversion from lower/higher precision floating formats is performed by this profile.
### 0.D Ordering and Tie-Break Policy
- Map keys MUST be sorted in ascending lexicographic order of their canonical encoded key bytes (RFC 8949 canonical ordering).
### 0.D.1 Context Independence Rule
- Canonical encoding is context-free and MUST NOT depend on usage (no signed/hash-critical or commitment-path dependent encoding variants).
### 0.E Parallel, Concurrency, and Reduction Policy
- Encoding output must be deterministic independent of thread scheduling.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE`.
### 0.G Operator Manifest
- `Glyphser.Serialization.EncodeCanonicalCBOR`
- `Glyphser.Serialization.ValidateCanonicalCBOR`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Canonical profile identifier: `CanonicalSerialization`.
### 0.I Outputs and Metric Schema
- `EncodeCanonicalCBOR` output: `(canonical_bytes)`.
- `ValidateCanonicalCBOR` output: `(validation_report)`.
### 0.J Spec Lifecycle Governance
- Any rule change is MAJOR.
### 0.K Failure and Error Semantics
- `EncodeCanonicalCBOR` MUST fail via deterministic error signaling (language-appropriate exception/error result) on invalid input under this profile.
- `ValidateCanonicalCBOR` MUST return `validation_report.valid=false` with deterministic error entries for any violation.
- Callers MUST treat any failure signal or `valid=false` report as nonconformant and MUST NOT use produced bytes for commitments/signatures.
### 0.L Input/Data Provenance
- Input schema and profile id must be declared with hash.

### 0.M Input Data Model Preamble
- All inputs to operators in this document are values in the CBOR data model (RFC 8949 Section 2).
- Implementations MUST map internal language/runtime structures to this model without semantic loss before encoding/validation.

---
## 2) System Model
### I.A Persistent State
- `profile_rules`.
### I.B Inputs and Hyperparameters
- `typed_object` is a value in the CBOR data model (RFC 8949 Section 2), constrained by consuming schema rules.
- profile id.
### I.C Constraints and Feasible Set
- valid iff object can be encoded under all canonical constraints.
- input maps MUST be duplicate-free by key semantics before encoding.
### I.D Transient Variables
- serializer buffers and diagnostics.
### I.E Invariants and Assertions
- stable bytes for identical object semantics.

### II.F Canonical Rules (Normative)
- RFC 8949 canonical CBOR baseline with profile overrides below.
- Additional restrictions:
  - map keys must be UTF-8 strings,
  - encoder MUST NOT normalize Unicode (no NFC/NFD transformation step is applied by canonicalization),
  - where a consuming contract requires NFC validity, non-NFC strings MUST be rejected deterministically by that consuming contract before commitment/hashing,
  - string keys are compared and encoded as raw UTF-8 bytes of the provided code-point sequence,
  - map-key ordering MUST follow canonical encoded-key byte ordering (RFC 8949 canonical ordering),
  - integers (positive and negative) MUST be encoded in the shortest possible canonical form,
  - integer shortest-form examples: `0 -> 0x00`, `23 -> 0x17`, `24 -> 0x1818`, `-1 -> 0x20`,
  - disallow duplicate keys,
  - if input contains duplicate map keys, encoder MUST return deterministic contract-violation error,
  - forbid indefinite-length encodings for strings/arrays/maps,
  - text strings MUST be valid UTF-8; encoder SHALL reject invalid UTF-8 sequences,
  - length of definite-length byte strings and text strings MUST use shortest possible canonical form,
  - length of definite-length arrays and maps MUST use shortest possible canonical form,
  - byte strings MUST be encoded as definite-length major type 2,
  - simple values MUST encode canonically as `false -> 0xf4`, `true -> 0xf5`, `null -> 0xf6`,
  - simple values other than `false`, `true`, `null` are forbidden unless explicitly allowed by schema; when allowed they MUST use canonical single-byte encoding,
  - `null` SHALL appear only when explicitly allowed by schema; otherwise optional fields are omitted,
  - forbid CBOR tags unless explicitly enumerated by consuming schema,
  - if input contains a tag not explicitly allowed by the consuming schema, encoder MUST return deterministic contract-violation error,
  - when a tag is permitted, it MUST use shortest canonical tag encoding (examples: tag 1 -> `0xc1`, tag 23 -> `0xd7`, tag 24 -> `0xd818`),
  - bignums are forbidden by default; if schema explicitly permits tags 2/3, they MUST use shortest canonical tag encoding and definite-length canonical byte strings with no leading zero bytes in the absolute-value representation,
  - floating-point values are encoded as IEEE-754 binary64 (major type 7, additional info 27, then 8 bytes network order),
  - `+Infinity` canonical bits: `0x7ff0000000000000`,
  - `-Infinity` canonical bits: `0xfff0000000000000`,
  - `NaN` canonical bits: `0x7ff8000000000000` (quiet NaN, zero payload); all other NaN payload bit patterns are forbidden,
  - every float is encoded as binary64 regardless of usage context,
  - signed zero is preserved (`+0.0 -> 0x0000000000000000`, `-0.0 -> 0x8000000000000000`),
  - fixed-length digest fields (`bytes32`, `bytes64`) must match required lengths,
  - encoder SHALL validate fixed-length byte fields (e.g., `bytes32`, `bytes64`) and fail deterministically on length mismatch,
  - optional fields absent are encoded by key omission (never implicit `null`),
  - empty map MUST encode as `0xa0`,
  - nonconformant CBOR is a deterministic `CONTRACT_VIOLATION`.

### II.G Commitment Rule (Normative)
- All signatures and commitment hashes MUST use:
  - `SHA-256(CBOR_CANONICAL(commit_array))`
- `commit_array` is always a CBOR array of exactly two elements:
  - element 0: domain-separation tag,
  - element 1: committed data object.
- Domain-separation tag MUST be the first element of `commit_array`.
- If the committed data object is itself an array, it remains nested as element 1 (no flattening).
- Domain-separation tag is a CBOR data item defined by the higher-level protocol using this profile (commonly integer or byte string), and it MUST itself follow all canonical rules in this document.
- Canonical helper:
  - `CommitHash(domain_tag, data_object) := SHA-256(CBOR_CANONICAL([domain_tag, data_object]))`.
- Prohibition:
  - Any signature/commitment definition that hashes `CBOR_CANONICAL(...)` with an outer array length not equal to 2 is a deterministic `CONTRACT_VIOLATION`.
- Object digest distinction:
  - A plain object digest is `ObjectDigest(data_object) := SHA-256(CBOR_CANONICAL(data_object))` and is not domain-separated.
  - Contracts MUST explicitly label each hash identity as either `CommitHash` (domain-separated) or `ObjectDigest` (plain digest).
  - Fields bound into certificates, replay identities, and release gates MUST use the hash type declared by their defining contract and MUST NOT be reinterpreted across types.

### II.H Conformance Vectors (Normative)
- Implementations MUST pass canonicalization vectors for key ordering, integer shortest-form encoding, float consistency, simple-value encoding, and optional-field semantics.
- Minimum required vectors:
  - mixed key lengths and UTF-8 multibyte keys,
  - nested maps with independently canonicalized key ordering,
  - integer shortest-form cases (e.g., `0`, `23`, `24`, `255`, `256`, `-1`, `-24`, `-25`),
  - float binary64 encoding stability,
  - float special values (`+Infinity`, `-Infinity`, canonical `NaN`) and rejection of non-canonical NaN payloads,
  - signed zero cases (`+0.0` vs `-0.0`),
  - simple values canonical bytes (`false`, `true`, `null`),
  - optional field omission vs explicit `null` when schema allows null,
  - tag shortest-form encoding and bignum allow/deny behavior,
  - empty map encoding (`0xa0`),
  - commitment-array two-element structure (`[domain_tag, data_object]`) without array flattening.
  - duplicate-key detection and deterministic rejection,
  - invalid UTF-8 text string rejection.

---
## 3) Initialization
1. Load profile rules.
2. Validate encoder/decoder implementation.
3. Initialize deterministic buffer policy.

---
## 4) Operator Manifest
- `Glyphser.Serialization.EncodeCanonicalCBOR`
- `Glyphser.Serialization.ValidateCanonicalCBOR`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Serialization.EncodeCanonicalCBOR`  
**Category:** Serialization  
**Signature:** `(typed_object -> canonical_bytes)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** produces canonical CBOR bytes under profile rules.

**Operator:** `Glyphser.Serialization.ValidateCanonicalCBOR`  
**Category:** Serialization  
**Signature:** `(typed_object, canonical_bytes -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates encoding equivalence and canonical constraints.
**Validation requirements:** MUST reject duplicate map keys and report deterministic violation diagnostics.
**Validation semantics:** decodes `canonical_bytes` under this profile, checks semantic equality with `typed_object` using CBOR-data-model identity rules (including distinctions for signed zero, NaN bit patterns, and integer-vs-float number types), and verifies all canonical constraints (ordering, definite lengths, shortest-form integers/tags, special-value rules).
**Validation report schema (minimum):**
```yaml
validation_report:
  valid: bool
  errors: [string]   # deterministic order
```
**Validation error signaling rule:** validation failures are communicated through `validation_report` (`valid=false`, non-empty `errors`). Implementations should avoid throwing exceptions for canonical violations unless the host runtime requires it.

---
## 6) Procedure
```text
1. Call EncodeCanonicalCBOR on typed_object; return canonical_bytes on success.
2. Optionally call ValidateCanonicalCBOR(typed_object, canonical_bytes) when validation evidence is required.
3. If validation is executed, return validation_report separately from canonical_bytes (operator outputs remain independent per Section 0.I).
```

---
## 7) Trace & Metrics
### Logging rule
- Serialization emits deterministic validation diagnostics.
### Trace schema
- `run_header`: profile_version
- `iter`: object_id, status
- `run_end`: canonical_hash
### Metric schema
- `encoded_objects`, `canonical_failures`
### Comparability guarantee
- Comparable iff profile version is identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- canonical constraints enforced without exceptions.
#### VII.B Operator test vectors (mandatory)
- map ordering, integer shortest-form, float/signed-zero, tag/bignum policy, duplicate-key rejection, optional-absence vectors.
#### VII.C Golden traces (mandatory)
- golden canonical byte snapshots.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for canonical bytes and hash outputs.
#### VIII.B Allowed refactor categories
- implementation refactors preserving byte output.
#### VIII.C Equivalence test procedure (mandatory)
- byte-for-byte compare against golden vectors.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- profile id and serializer implementation hash.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- identical canonical bytes after restore.
