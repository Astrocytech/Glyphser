# Glyphser Determinism Profiles Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Replay.DeterminismProfiles`  
**Purpose (1 sentence):** Define normative determinism profiles (`BITWISE`, `TOLERANCE`) with machine-checkable runtime constraints and replay comparison rules.  
**Spec Version:** `Glyphser.Replay.DeterminismProfiles` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Reproducibility profile governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Replay.DeterminismProfiles`
- **Purpose (1 sentence):** Determinism profile specification.

### 0.A Objective Semantics
- This contract performs deterministic validation/comparison only; no optimization objective applies.
- Objective type: N/A.
- Primary comparison rule: exact profile conformance plus profile-defined replay comparison.
- Invalid objective policy: profile mismatch is deterministic failure.

### 0.B Reproducibility Contract
- Replayable given `(determinism_profile_id, determinism_profile_hash, backend_binary_hash, driver_runtime_fingerprint_hash, trace_a_hash, trace_b_hash)`.

### 0.C Numeric Policy
- This section also defines deterministic equivalence-level semantics used by replay comparison.
- `BITWISE` profile uses strict bitwise equality for compared values.
- `TOLERANCE` profile uses explicit per-field tolerance policies.
- Equivalence levels (normative):
  - `E0`: byte-identical outputs (`verdict`, hash fields, and all machine-readable report fields not governed by `E1` tolerance comparison).
  - `E1`: numerically equivalent under declared tolerance map (`abs_tol`, `rel_tol`, `nan_policy`).

### 0.D Ordering and Tie-Break Policy
- Reduction ordering behavior must be declared in `profile_rules`.
- If the profile allows multiple valid orderings, the concrete ordering used MUST be captured in trace metadata.
- If the profile fixes ordering, trace capture is optional and treated as redundant metadata.

### 0.E Parallel, Concurrency, and Reduction Policy
- Profile declares collective algorithm, chunk ordering, and atomic policy.

### 0.F Environment and Dependency Policy
- `determinism_profile_hash` is required in replay token and certificate payload.

### 0.G Operator Manifest
- `Glyphser.Replay.ValidateDeterminismProfile`
- `Glyphser.Replay.CompareByProfile`
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- Profile registry path: `contracts/determinism_profiles.cbor`.

### 0.I Outputs and Metric Schema
- Outputs: `(profile_report, comparison_report)`.
- Metrics:
  - `profile_violations`: count of runtime/profile rule violations in `ValidateDeterminismProfile`.
  - `e0_mismatch_count`: count of exact mismatches under `BITWISE`.
  - `e1_out_of_band_count`: count of value comparisons exceeding declared `abs_tol/rel_tol` under `TOLERANCE`.

### 0.J Spec Lifecycle Governance
- Profile semantics changes are MAJOR.

### 0.K Failure and Error Semantics
- Emit deterministic `REPLAY_DIVERGENCE` on comparison failure.
- If `profile_id` is not found by `CompareByProfile`, emit deterministic `REPLAY_DIVERGENCE` and abort comparison.

### 0.L Input/Data Provenance
- Profile definitions are hash-addressed.

---
## 2) System Model
### I.A Persistent State
- determinism profile registry.

### I.B Inputs and Hyperparameters
- profile id, trace pair, backend/runtime metadata.
- `runtime_metadata` MUST conform exactly to `DriverRuntimeFingerprint` schema in §II.H (missing/extra fields are violations).

### I.C Constraints and Feasible Set
- valid iff runtime metadata satisfies selected profile.
- traces MUST conform to the external trace-format contract (`Glyphser.Trace.Format`) and support deterministic field-path traversal.
- `Glyphser.Trace.Format` MUST provide trace metadata fields `collective_algorithm_id`, `collective_chunking_policy`, and `rank_order_policy`; without these fields, profile-conformant comparison is not defined.

### I.D Transient Variables
- comparison diagnostics.

### I.E Invariants and Assertions
- one deterministic verdict per `(profile, trace_a_hash, trace_b_hash)`.

### II.F Profile Definitions and Rules Schema (Normative)
- `determinism_profile_id`: enum(`BITWISE`, `TOLERANCE`).
- `profile_rules` canonical CBOR schema (tagged union by `determinism_profile_id`):
  - profile-rules closure rule: only fields listed below are permitted (no extras).
  - common fields:
    - `profile_id:string`
      - MUST equal top-level `determinism_profile_id` used for hash input.
    - `rules_version:uint32` (MUST be `1` for this contract version)
    - `backend_binary_hash:bytes32`
    - `driver_runtime_equivalence_set:array<bytes32>` (sorted unique set of acceptable `driver_runtime_fingerprint_hash` values).
    - `collective_algorithm_id:string`
    - `collective_chunking_policy:string`
    - `rank_order_policy:string`
  - `BITWISE` required fields:
    - `deterministic_kernels_required:bool` (MUST be true)
    - `allow_nondeterministic_atomics:bool` (MUST be false)
    - `accumulation_policy:enum("FIXED_DTYPE_FIXED_ORDER","FLOAT32_SEQ","FLOAT64_SEQ")` (must be fixed by profile; deviation is mismatch)
    - `runtime_flags:map<string,string>` (exact key/value runtime flags)
    - `deterministic_primitive_allowlist_hash:bytes32`
  - `TOLERANCE` required fields:
    - `tolerance_map:map<string,ToleranceRule>` (keys are exact dot-separated field/key paths; duplicate keys are forbidden)
    - `default_compare_policy:enum("E0")` (fields not listed in `tolerance_map` use strict equality)
    - `missing_field_policy:enum("MISMATCH","IGNORE")`
    - `shape_mismatch_policy:enum("MISMATCH")`
- `ToleranceRule` schema:
  - `{abs_tol:float64, rel_tol:float64, nan_policy:enum("FORBID","EQUAL_IF_BOTH_NAN")}`.
- `ToleranceRule` constraints:
  - `abs_tol` and `rel_tol` MUST be non-negative finite float64 values; negative or non-finite values invalidate profile.
- `deterministic_primitive_allowlist_hash` computation:
  - `SHA-256(CBOR_CANONICAL(primitive_allowlist))`, where `primitive_allowlist` is a sorted unique array of primitive-id strings.
  - primitive-id strings MUST use exact backend canonical names from backend documentation/build metadata (no alias expansion).
- `driver_runtime_equivalence_set` note:
  - if empty, no runtime fingerprint can satisfy the profile; validation deterministically fails with `FINGERPRINT_NOT_ALLOWED`.

### II.G Profile Hash and Comparator Rules (Normative)
- `determinism_profile_hash = SHA-256(CBOR_CANONICAL([determinism_profile_id, profile_rules]))`.
- deterministic traversal order (normative):
  - maps/dictionaries: visit keys in ascending UTF-8 bytewise lexicographic order,
  - arrays: visit elements in increasing index order,
  - nested structures: traverse depth-first,
  - array element path form: `parent_path.i` (dot plus decimal index).
- `TOLERANCE` numeric comparison:
  - given expected `a`, observed `b`:
    - if both are `+inf`, match; if both are `-inf`, match; differing infinity sign is mismatch,
    - mismatch if either is NaN and `nan_policy="FORBID"`,
    - match if both are NaN and `nan_policy="EQUAL_IF_BOTH_NAN"`,
    - mismatch if exactly one is NaN,
    - `+0.0` and `-0.0` are considered equal under `TOLERANCE`,
    - otherwise match iff `|a-b| <= max(abs_tol, rel_tol * max(|a|, |b|))`.
    - note: if `rel_tol * max(|a|,|b|)` overflows to infinity, comparison for that field effectively passes whenever `|a-b|` is finite.
- Structural comparison rules:
  - missing fields:
    - a field/key is missing if present in one trace and absent in the other (symmetric definition),
    - if `missing_field_policy="MISMATCH"` then mismatch,
    - if `missing_field_policy="IGNORE"` then field/key is excluded from comparison.
  - mismatched shapes/types always mismatch under `shape_mismatch_policy="MISMATCH"`.
  - for shape mismatches (including array length mismatch), mismatch `path` MUST identify the parent field where shape mismatch occurs.
  - nested structures compare recursively by field/key path.
  - tolerance-map path matching is exact string equality against the compared field/key path; no wildcard or prefix matching is permitted.
  - for nested dynamic-key maps, each key is treated as a field; missing-key handling uses `missing_field_policy` at that nesting level.
  - for non-floating scalar types (int/bool/string/bytes), comparison is strict equality (`E0`) even under `TOLERANCE`.
  - `default_compare_policy` applies per leaf value: any leaf path without an exact `tolerance_map` key match uses `E0`.
  - implementations MAY report unused `tolerance_map` keys as diagnostics; such diagnostics MUST NOT affect verdict.

### II.H Machine-Checkable Runtime Capture (Normative)
- `DriverRuntimeFingerprint` canonical CBOR map schema (authoritative):
  - `gpu_model:string`
  - `gpu_sm_count:uint32` (number of streaming multiprocessors)
  - `driver_version:string`
  - `cuda_version:string`
  - `cudnn_version:string`
  - `cublas_version:string`
  - `nccl_version:string`
  - `os_kernel_version:string`
  - `compiler_id:string`
  - `compiler_flags_hash:bytes32`
  - `backend_adapter_version:string`
  - `backend_build_id:string`
  - `primitive_allowlist_used_hash:bytes32` (hash of primitive allowlist actually enforced at runtime)
  - `deterministic_kernels_enabled:bool` (runtime deterministic-kernel mode)
  - `nondeterministic_atomics_used:bool` (runtime observed/allowed nondeterministic atomics usage)
  - `runtime_flags:map<string,string>` (effective runtime flags used during execution)
  - `accumulation_policy:enum("FIXED_DTYPE_FIXED_ORDER","FLOAT32_SEQ","FLOAT64_SEQ")` (effective accumulation policy used during execution)
- `driver_runtime_fingerprint_hash = SHA-256(CBOR_CANONICAL(driver_runtime_fingerprint_map))`.
- `compiler_flags_hash` computation:
  - `compiler_flags_hash = SHA-256(CBOR_CANONICAL(sorted_unique_compiler_flags_array))`.
  - `sorted_unique_compiler_flags_array` is sourced from the canonical backend build record of compiler invocations for the shipped backend binary.
  - each element is a UTF-8 string representing one compiler CLI token exactly as recorded (for example `-O2`, `-DNAME=VALUE`);
  - array normalization is limited to byte-exact UTF-8 preservation, bytewise sort, and duplicate removal; no additional Unicode normalization is applied.
- Canonical map-key ordering is inherited from `docs/layer1-foundation/Canonical-CBOR-Profile.md`.
- `primitive_allowlist_used_hash` is checked for `BITWISE` profiles; for `TOLERANCE` profiles it is ignored.

---
## 3) Initialization
1. Load profile registry.
2. Validate selected profile id and `profile_rules` schema.
3. Validate runtime metadata against selected profile constraints.

---
## 4) Operator Manifest
- `Glyphser.Replay.ValidateDeterminismProfile`
- `Glyphser.Replay.CompareByProfile`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Replay.ValidateDeterminismProfile`  
**Category:** Replay  
**Signature:** `(profile_id, runtime_metadata, backend_binary_hash -> profile_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates runtime/backend conformance to selected profile, including:
- profile existence by `profile_id`,
- `profile_rules.rules_version == 1` (unsupported versions are invalid),
- exact `runtime_metadata` conformance to §II.H schema (including no extra fields and no missing required fields),
- recomputed `driver_runtime_fingerprint_hash` membership in `driver_runtime_equivalence_set`,
- provided `backend_binary_hash == profile_rules.backend_binary_hash`,
- for `BITWISE`, exact equality of `runtime_metadata.runtime_flags` and `profile_rules.runtime_flags`,
- for `BITWISE`, exact equality of `runtime_metadata.accumulation_policy` and `profile_rules.accumulation_policy`,
- for `BITWISE`, exact equality of `runtime_metadata.primitive_allowlist_used_hash` and `profile_rules.deterministic_primitive_allowlist_hash`,
- for `BITWISE`, `runtime_metadata.deterministic_kernels_enabled == true`,
- for `BITWISE`, `runtime_metadata.nondeterministic_atomics_used == false`.  
**`profile_report` minimum schema (canonical CBOR map):**
- `is_valid:bool`
- `profile_id:string`
- `determinism_profile_hash?:bytes32` (present iff profile is found and loaded)
- `driver_runtime_fingerprint_hash?:bytes32` (present iff runtime metadata can be parsed well enough to compute fingerprint hash)
- `violations:array<{path:string, code:enum("PROFILE_NOT_FOUND","PROFILE_RULE_VIOLATION","FINGERPRINT_NOT_ALLOWED","INVALID_TOLERANCE_RULE","RUNTIME_METADATA_SCHEMA_ERROR","BACKEND_BINARY_MISMATCH","RUNTIME_FLAGS_MISMATCH","ACCUMULATION_POLICY_MISMATCH","PRIMITIVE_ALLOWLIST_MISMATCH","DETERMINISTIC_KERNELS_MISMATCH","ATOMICS_POLICY_MISMATCH","UNSUPPORTED_RULES_VERSION")}>` (sorted by `(path, code)` bytewise ascending)
- violation `path` semantics:
  - `path` is dot-separated into `runtime_metadata` for field-specific violations,
  - `path=""` (empty string) for global violations not tied to one metadata field (for example `PROFILE_NOT_FOUND`).
  - if multiple violations share identical `(path, code)`, relative order is implementation-defined but MUST be deterministic for identical inputs.

**Operator:** `Glyphser.Replay.CompareByProfile`  
**Category:** Replay  
**Signature:** `(trace_a, trace_b, profile_id -> comparison_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** compares traces under profile-specific `E0/E1` rules.  
If `profile_id` is missing from registry, emit `REPLAY_DIVERGENCE` and abort.
If selected `profile_rules.rules_version != 1`, emit `REPLAY_DIVERGENCE` and abort.
Trace metadata MUST include `collective_algorithm_id`, `collective_chunking_policy`, and `rank_order_policy`; values MUST match selected `profile_rules` bytewise. Missing or mismatching fields are recorded with `reason_code="PROFILE_RULE_VIOLATION"`.
**`comparison_report` minimum schema (canonical CBOR map):**
- `verdict:enum("MATCH","MISMATCH")`
- `profile_id:string`
- `determinism_profile_hash:bytes32`
- `e0_mismatch_count:uint64`
- `e1_out_of_band_count:uint64`
- `mismatches:array<{check_id:string, path:string, reason_code:enum("E0_MISMATCH","E1_OUT_OF_BAND","MISSING_FIELD","SHAPE_MISMATCH","NAN_FORBIDDEN","TYPE_MISMATCH","PROFILE_RULE_VIOLATION")}>` (sorted by `(check_id, path, reason_code)` bytewise ascending)
- path convention:
  - `path` is dot-separated field/key path (for example `step_0.layer1.weight`).
- check-id convention:
  - `check_id` uniquely identifies a comparison point in deterministic traversal (for example `step_0/loss`, `step_3/layer1.weight`).
  - generation MUST be deterministic from traversal position/path (for example derived from path plus traversal index), and reproducible for identical inputs and traversal order.
- path escaping rule (normative, applies to report `path`, `iter.path`, and `tolerance_map` keys):
  - segment join delimiter is `.`.
  - escape character is `\\`.
  - while encoding a segment: literal `\\` MUST be encoded as `\\\\`; literal `.` MUST be encoded as `\\.`.
  - while decoding: only `\\.` and `\\\\` are valid escape sequences; any other escaped byte or trailing `\\` is deterministic `CONTRACT_VIOLATION`.
  - round-trip invariant MUST hold: `decode_path(encode_path(segments)) == segments`.
  - tolerance-map path matching uses exact bytewise equality on encoded path strings.
  - `Glyphser.Trace.Format` implementations MUST implement this exact path encoding/decoding rule.

---
## 6) Procedure
```text
1. ValidateDeterminismProfile
2. CompareByProfile
3. Return profile_report + comparison_report
```

---
## 7) Trace & Metrics
### Logging rule
- profile checks and replay comparisons emit deterministic records.

### Trace schema
- `run_header`: `{profile_id:string, determinism_profile_hash:bytes32}`
- `iter`: `{check_id:string, status:enum("MATCH","MISMATCH"), path:string?}`
- `run_end`: `{comparison_status:enum("MATCH","MISMATCH")}`
- `iter.path`, when present, follows the same dot-separated convention as report `path`.

### Metric schema
- `profile_violations`, `e0_mismatch_count`, `e1_out_of_band_count`

### Comparability guarantee
- Comparable iff `determinism_profile_id` and `determinism_profile_hash` are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- selected profile must declare runtime constraints and comparator policy.
- `profile_rules` and `ToleranceRule` schemas must validate.
- `runtime_metadata` must validate exactly against §II.H schema (no missing/extra fields).
- `profile_rules.rules_version` must equal `1`; otherwise emit `UNSUPPORTED_RULES_VERSION`.
- runtime check: `driver_runtime_fingerprint_hash` must match recomputed fingerprint hash and be allowed by `driver_runtime_equivalence_set`.
- runtime check: provided `backend_binary_hash` must equal `profile_rules.backend_binary_hash`.
- runtime check (`BITWISE`): `runtime_metadata.runtime_flags` must equal `profile_rules.runtime_flags`.
- runtime check (`BITWISE`): `runtime_metadata.accumulation_policy` must equal `profile_rules.accumulation_policy`.
- runtime check (`BITWISE`): `runtime_metadata.primitive_allowlist_used_hash` must equal `profile_rules.deterministic_primitive_allowlist_hash`.
- runtime check (`BITWISE`): `runtime_metadata.deterministic_kernels_enabled` must be `true`.
- runtime check (`BITWISE`): `runtime_metadata.nondeterministic_atomics_used` must be `false`.

#### VII.B Operator test vectors (mandatory)
- profile pass/fail fixtures and mixed hardware scenarios.

#### VII.C Golden traces (mandatory)
- golden profile-conformance traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- `E0` required for `verdict`, hash fields, and deterministic machine-readable report fields.
- `E1` allowed only for value-level numeric comparisons under `TOLERANCE`.

#### VIII.B Allowed refactor categories
- comparator implementation refactors preserving outputs.

#### VIII.C Equivalence test procedure (mandatory)
- exact compare for all `E0` fields; tolerance compare for `E1` fields.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- `profile_id:string`
- `determinism_profile_hash:bytes32`
- `trace_a_hash:bytes32`
- `trace_b_hash:bytes32`
- `comparator_cursor:{check_index:uint64, path:string}`.

### Cursor semantics
- `check_index` is the 0-based index of next comparison check.
- `path` is the exact path of the next comparison point in deterministic traversal order.
- `(check_index, path)` combination MUST uniquely identify the next comparison point.
- if `check_index >= total_comparison_points` on restore, comparison is treated as complete and final verdict/report are returned immediately.

### Serialization
- deterministic canonical CBOR.

### Restore semantics
- resumed comparison from `comparator_cursor` MUST yield the same final verdict and report as full rerun.
- `trace_a` and `trace_b` are assumed content-addressed artifacts retrievable by `trace_a_hash`/`trace_b_hash` from external storage (out of scope of this contract).
