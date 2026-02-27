# Glyphser Environment Manifest Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Environment.Manifest`  
**Purpose (1 sentence):** Define canonical environment/runtime fingerprint schema and hashing used by replay tokens, checkpoints, and certificates.  
**Spec Version:** `Glyphser.Environment.Manifest` | 2026-02-20 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Deterministic environment identity and compatibility gating.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Environment.Manifest`
- **Purpose (1 sentence):** Canonical environment identity contract.

### 0.A Objective Semantics
- This contract performs deterministic capture/validation only; no optimization objective applies.
- Primary comparison rule: exact hash equality and fieldwise compatibility checks.

### 0.B Reproducibility Contract
- Replayable given `(env_manifest_hash)` with content-addressable retrieval of the committed manifest bytes.
- Required normative dependencies for deterministic replay:
  - `docs/layer1-foundation/Canonical-CBOR-Profile.md`
  - `docs/layer1-foundation/Determinism-Profiles.md`
  - `docs/layer1-foundation/Error-Codes.md`
- Dependency availability rule:
  - if a required dependency document is missing, unreadable, or its content does not match the version/sections referenced by this contract, treat as fatal configuration error and abort with `CONTRACT_VIOLATION`.
  - dependency governance assumption: referenced documents MUST be maintained as a coherent suite with this contract.

### 0.C Numeric Policy
- This section also defines equivalence-level semantics for compatibility and manifest commitments.
- All fields are exact typed values.
- `E0` (normative): byte-identical canonical manifest bytes, `env_manifest_hash`, and compatibility verdict/report fields.

### 0.D Ordering and Tie-Break Policy
- Canonical CBOR encoding is mandatory.
- Canonical CBOR is defined by RFC 8949 deterministic encoding rules and `docs/layer1-foundation/Canonical-CBOR-Profile.md`.

### 0.E Parallel, Concurrency, and Reduction Policy
- Runtime capture may be parallelized.
- Final manifest map and hash MUST be deterministic.

### 0.F Environment and Dependency Policy
- Determinism level for manifest commitment: `BITWISE`.

### 0.G Operator Manifest
- `Glyphser.Environment.BuildManifest`
- `Glyphser.Environment.ComputeManifestHash`
- `Glyphser.Environment.ValidateCompatibility`
- `Glyphser.Error.Emit` (defined in `docs/layer1-foundation/Error-Codes.md`)

### 0.H Namespacing and Packaging
- Namespace: `Glyphser.Environment.*`
- Canonical manifest artifact path: `contracts/environment_manifest.cbor`

### 0.I Outputs and Metric Schema
- Outputs: `(env_manifest, env_manifest_hash, compatibility_report)`.
- `BuildManifest` outputs `env_manifest`.
- `ComputeManifestHash` outputs `env_manifest_hash`.
- `ValidateCompatibility` outputs `compatibility_report`.

### 0.J Spec Lifecycle Governance
- Required field changes are MAJOR.

### 0.K Failure and Error Semantics
- If a required capture source is unavailable or a required field cannot be computed, emit deterministic `CONTRACT_VIOLATION` and abort.
- If a required command source executes with non-zero exit status or emits no output when output is required, emit `CONTRACT_VIOLATION` and abort.
- `CONTRACT_VIOLATION` emission semantics are governed by `docs/layer1-foundation/Error-Codes.md`.

### 0.L Input/Data Provenance
- Capture sources MUST be recorded deterministically via the normalized manifest fields and constituent hashes.

### 0.Z EQC Mandatory Declarations Addendum
- No stochastic operators in this contract version.
- Determinism level: `BITWISE` for canonical manifest bytes and `env_manifest_hash`.
- Numeric edge policy:
  - This contract does not define floating stochastic computation paths; numeric handling is exact typed capture and canonical encoding per declared rules.

---
## 2) System Model
### I.A Persistent State
- Environment manifest registry keyed by `env_manifest_hash`.

### I.B Inputs and Hyperparameters
- `BuildManifest` takes no explicit inputs: it deterministically captures host/runtime facts from normative sources.
- `ValidateCompatibility` takes `(candidate_manifest, required_manifest?)`.
- `required_manifest` MUST conform to the same schema as section 2.6 (complete required manifest, no extra fields).
- Backend adapter definition: the component that interfaces with the compute/runtime backend and exposes deterministic metadata APIs used by this contract.

### I.C Constraints and Feasible Set
- Valid iff all required fields exist, satisfy schema/type constraints, and per-field normalization rules.
- Capture MUST observe a consistent snapshot of sources; if snapshot consistency cannot be guaranteed, capture aborts with `CONTRACT_VIOLATION`.
- For multi-file artifact hashing, all file contents MUST be read from one consistent snapshot view; if mutation is detected during capture, abort with `CONTRACT_VIOLATION`.
- Multi-file mutation detection algorithm (normative):
  1. resolve symlinks to final regular-file targets and record per-target `(mtime,size)`,
  2. read all resolved target files and compute per-file `sha256(content)`,
  3. re-resolve symlinks to current targets; if any current resolved path differs from the path recorded in step 1, abort with `CONTRACT_VIOLATION`; otherwise re-check `(mtime,size)` for all current targets,
  4. if any metadata changed, abort with `CONTRACT_VIOLATION`,
  5. if metadata unchanged, re-read each current target file and recompute sha256; if any hash differs from step 2, abort with `CONTRACT_VIOLATION`.
  - note: if a symlink target is replaced by another file with identical metadata and identical content, this change is undetectable by this algorithm and accepted as a practical determinism trade-off.

### I.D Transient Variables
- Capture diagnostics and validation diagnostics.

### I.E Invariants and Assertions
- Same normalized runtime facts always produce identical canonical CBOR bytes and `env_manifest_hash`.

### 2.6 Canonical Environment Manifest Schema (Normative)
- Top-level map MUST contain exactly these fields (no extras):
  - `schema_version:string` (MUST equal `Glyphser.Environment.Manifest`)
  - `os_name:string`
  - `os_version:string`
  - `kernel_version:string`
  - `hardware_arch:string`
  - `python_version:string`
  - `backend_adapter_version:string`
  - `backend_binary_hash:bytes32`
  - `driver_runtime_fingerprint_hash:bytes32`
  - `determinism_profile_hash:bytes32`
  - `toolchain_hash:bytes32`
  - `env_vars_fingerprint_hash:bytes32`
- Manifest map MUST be encoded using canonical CBOR key ordering (bytewise key order) per RFC 8949 deterministic encoding.

### 2.7 Field Capture and Normalization Rules (Normative)
- Command execution for OS/kernel/arch capture MUST use `LC_ALL=C`.
- Regex dialect:
  - all regular expressions in this contract use ECMAScript syntax.
- Executable-path definition:
  - a command path is executable iff it resolves to a regular file that the current process can execute.
- `uname` command path resolution algorithm (deterministic):
  1. if `UNAME_CMD` is set:
     - it MUST be an absolute path and executable;
     - otherwise capture failure (`CONTRACT_VIOLATION`);
     - use `UNAME_CMD`.
  2. else if `/bin/uname` is executable, use it.
  3. else if `/usr/bin/uname` is executable, use it.
  4. else capture failure (`CONTRACT_VIOLATION`).
- `os_name`:
  - source: `<resolved_uname_path> -s`
  - normalization: UTF-8, trim outer whitespace, lowercase ASCII.
- `kernel_version`:
  - source: `<resolved_uname_path> -r`
  - normalization: UTF-8, trim outer whitespace.
- `hardware_arch`:
  - source: `<resolved_uname_path> -m`
  - normalization: UTF-8, trim outer whitespace, lowercase ASCII.
  - architecture aliases are not remapped; normalized raw output is authoritative.
- `os_version`:
  - source priority:
    1. `/etc/os-release` `VERSION_ID`
    2. fallback `<resolved_uname_path> -v`
  - normalization: UTF-8, trim outer whitespace.
  - a source is considered failed if read fails or normalized value is empty.
  - both sources MUST be evaluated within the same capture snapshot window.
  - mutation detection for fallback chain:
    - if source 1 is read from `/etc/os-release`, resolve symlink to final regular-file target and record target metadata snapshot `(mtime,size)` plus sha256(content),
    - immediately before source 2 fallback, re-resolve target and re-check `(mtime,size)`; if changed, treat as mutation and abort,
    - if unchanged metadata, re-read resolved target and recompute hash; if hash differs, treat as mutation and abort.
  - if all sources fail, abort with `CONTRACT_VIOLATION`.
  - note: `/bin/uname -v` may include build metadata/timestamps; this is accepted as exact runtime identity in this version.
  - race-window note: execute fallback command immediately after metadata/hash re-check to minimize race exposure.
- `python_version`:
  - source: `platform.python_version()`
  - normalization algorithm:
    1. read raw version string `v`,
    2. apply regex `^([0-9]+)\\.([0-9]+)(?:\\.([0-9]+))?`,
    3. if group3 present, normalized value is `group1.group2.group3`,
    4. else normalized value is `group1.group2.0`,
    5. if regex does not match, abort.
  - captures the interpreter executing this contract.
- `backend_adapter_version`:
  - source: deterministic backend adapter API `adapter.get_version()`.
  - `adapter.get_version()` MUST return a UTF-8 string.
  - `adapter.get_version()` MUST be deterministic for identical backend installation/state.
  - normalization: UTF-8, trim outer whitespace.
  - empty normalized value is invalid and MUST abort with `CONTRACT_VIOLATION`.
- Normalization failures (invalid UTF-8, invalid format) are capture failures and MUST abort with `CONTRACT_VIOLATION`.

### 2.8 Constituent Hash Definitions (Normative)
- Hash algorithm for all fields below: SHA-256.
- `backend_binary_hash`:
  - backend adapter MUST expose deterministic API `adapter.get_canonical_artifact_set()` returning `(root_path, relative_paths[])`.
  - `adapter.get_canonical_artifact_set()` MUST be deterministic for identical backend installation/state.
  - `root_path` MUST be an absolute path; if relative, abort with `CONTRACT_VIOLATION`.
  - `root_path` MUST exist and be a directory; otherwise abort with `CONTRACT_VIOLATION`.
  - implementation MUST resolve `root_path` to canonical absolute path (`realpath`) before resolving artifacts; if canonical resolution fails (for example due to broken symlink path components), abort with `CONTRACT_VIOLATION`.
  - `root_path` is used for file resolution only and is not included in hash input.
  - `relative_paths[]` MUST be unique and sorted bytewise.
  - if `relative_paths[]` is empty, abort with `CONTRACT_VIOLATION`.
  - returned `relative_paths[]` set MUST be stable for identical backend installation/state.
  - implementation MUST normalize and validate adapter-returned paths before use under the rules below.
  - each `relative_path` MUST be UTF-8, trimmed, normalized to `/` separators, and relative to `root_path` (no absolute path, no `..` traversal, no duplicate separators).
  - `relative_path` MUST NOT start with `./` or contain `./` as a distinct path component.
  - after normalization, any remaining `..` path component is forbidden; if present, abort with `CONTRACT_VIOLATION`.
  - if normalized `relative_path` is empty, abort with `CONTRACT_VIOLATION`.
  - `relative_path` MUST NOT end with `/`.
  - paths MUST resolve to regular files; symlinks MUST be resolved to final regular-file targets before hashing.
  - unresolved/broken symlink, directory target, or any non-regular-file target is fatal and aborts.
  - if artifact set contains one file, hash raw bytes of that file.
  - if artifact set contains multiple files, hash canonical CBOR array of `(relative_path, file_sha256)` pairs sorted by `relative_path` bytewise.
- `driver_runtime_fingerprint_hash`:
  - input: canonical CBOR map for `DriverRuntimeFingerprint` from `docs/layer1-foundation/Determinism-Profiles.md` section II.H.
  - if dependency document is unavailable or invalid, abort with `CONTRACT_VIOLATION`.
- `determinism_profile_hash`:
  - input: selected profile commitment from `docs/layer1-foundation/Determinism-Profiles.md` section II.G.
  - if dependency document is unavailable or invalid, abort with `CONTRACT_VIOLATION`.
  - profile/fingerprint selection source is runtime environment configuration; selection MUST be deterministic and reproducible for identical configuration.
- `toolchain_hash`:
  - input: canonical CBOR map:
    - `c_compiler_id:string|null`
    - `c_compiler_version:string|null`
    - `cxx_compiler_id:string|null`
    - `cxx_compiler_version:string|null`
    - `linker_id:string|null`
    - `linker_version:string|null`
    - `build_system_id:string|null`
    - `build_system_version:string|null`
  - all keys MUST be present; map hashed via canonical CBOR.
  - capture sources and normalization:
    - tool path resolution is deterministic per tool:
      - C compiler: if `CC` is set, it MUST be absolute and executable; otherwise abort. If unset, use `/usr/bin/cc` only if executable, else treat as absent.
      - C++ compiler: if `CXX` is set, it MUST be absolute and executable; otherwise abort. If unset, use `/usr/bin/c++` only if executable, else treat as absent.
      - Linker: if `LD` is set, it MUST be absolute and executable; otherwise abort. If unset, use `/usr/bin/ld` only if executable, else treat as absent.
      - Build system: if `CMAKE_COMMAND` is set, it MUST be absolute and executable; otherwise abort. If unset, use `/usr/bin/cmake` only if executable, else treat as absent.
    - if tool is absent/unreadable, corresponding id/version pair MUST be set to `null` (runtime-only environments supported).
    - `c_compiler_id`, `c_compiler_version`: from resolved C compiler `--version` first matching line among first 5 lines when available.
      - parse rules (in order):
        1. if matches `^clang version ([0-9]+\\.[0-9]+\\.[0-9]+)`, set id=`clang`, version=group1,
        1a. if matches `^Apple clang version ([0-9]+\\.[0-9]+(\\.[0-9]+)?)`, set id=`apple-clang`, version=`group1` padded to three segments by appending `.0` for missing segment,
        2. else if matches `^([A-Za-z0-9_+.-]+).*?([0-9]+\\.[0-9]+\\.[0-9]+)`, set id=group1, version=group2,
        3. else if matches `^([A-Za-z0-9_+.-]+).*?([0-9]+\\.[0-9]+)`, set id=group1, version=`group2.0`,
        4. else abort.
    - `cxx_compiler_id`, `cxx_compiler_version`: from resolved C++ compiler `--version` first matching line among first 5 lines using same parse rules as C compiler.
    - `linker_id`, `linker_version`: from resolved linker `--version` first matching line among first 5 lines when available.
      - parse rules (in order):
        1. if matches `^(LLD|lld) ([0-9]+\\.[0-9]+\\.[0-9]+)`, set id=`lld`, version=group2,
        2. else if matches `^GNU ld .*?([0-9]+\\.[0-9]+(\\.[0-9]+)?)`, set id=`gnu-ld`, version=group1,
        3. else if matches `^([A-Za-z0-9_+.-]+).*?([0-9]+\\.[0-9]+\\.[0-9]+)`, set id=group1, version=group2,
        3a. else if matches `^([A-Za-z0-9_+.-]+).*?([0-9]+\\.[0-9]+)`, set id=group1, version=`group2.0`,
        4. else abort.
    - `build_system_id`, `build_system_version`: from resolved build-system tool `--version` first matching line among first 5 lines when available.
      - parse rules (in order):
        1. if matches `^cmake version ([0-9]+\\.[0-9]+\\.[0-9]+)`, set id=`cmake`, version=group1,
        2. else if matches `^cmake version ([0-9]+\\.[0-9]+)`, set id=`cmake`, version=`group1.0`,
        3. else abort.
  - all parsed strings MUST be UTF-8, trimmed, and lowercase ASCII for ids; versions preserve normalized dotted/semver token.
  - version-normalization note:
    - version width normalization is rule-specific (some capture rules preserve two-part versions, others pad to three parts);
    - cross-tool version strings are not globally normalized to one width in this contract version.
  - compiler-id canonicalization post-process:
    - if parsed id contains `gcc` (case-insensitive), canonical id=`gcc`,
    - if parsed id contains `g++` (case-insensitive), canonical id=`gcc`,
    - if parsed id contains `clang` and not `apple clang`, canonical id=`clang`,
    - apple clang remains `apple-clang`.
  - build-system scope note: this version captures CMake only; other build systems are represented as `null` unless surfaced via `CMAKE_COMMAND`.
  - parse failure for an available tool is fatal and aborts with `CONTRACT_VIOLATION`.
- `env_vars_fingerprint_hash`:
  - input variable-name allowlist (exact names, fixed order after bytewise sort):
    - `PYTHONHASHSEED`
    - `CUDA_VISIBLE_DEVICES`
    - `CUBLAS_WORKSPACE_CONFIG`
    - `OMP_NUM_THREADS`
    - `MKL_NUM_THREADS`
    - `OPENBLAS_NUM_THREADS`
    - `NUMEXPR_NUM_THREADS`
    - `NCCL_ALGO`
    - `NCCL_PROTO`
    - `TF_DETERMINISTIC_OPS`
  - canonical value map MUST contain all allowlisted keys exactly once: `{var_name: value_or_null}`.
  - unset vars MUST be encoded as CBOR `null` (`0xf6`).
  - set vars MUST be valid UTF-8 text; invalid UTF-8 values are fatal capture failures.
  - if an environment-variable value exceeds `1048576` bytes (1 MiB), abort with `CONTRACT_VIOLATION`.
  - hash input is canonical CBOR of that map.
  - this allowlist is the canonical set for `Glyphser.Environment.Manifest`; extensions require a MAJOR version change.
- Constituent hash failure rule:
  - any failure during constituent hash computation (read error, parse error, algorithm failure) is fatal and aborts with `CONTRACT_VIOLATION`.

---
## 3) Initialization
1. Capture required runtime facts from normative sources.
2. Normalize fields per section 2.7.
3. Compute constituent hashes per section 2.8.
4. Assemble schema-valid manifest map.
5. Compute `env_manifest_hash`.

---
## 4) Operator Manifest
- `Glyphser.Environment.BuildManifest`
- `Glyphser.Environment.ComputeManifestHash`
- `Glyphser.Environment.ValidateCompatibility`
- `Glyphser.Error.Emit`
- External operator reference note: `Glyphser.Error.Emit` is defined in `docs/layer1-foundation/Error-Codes.md`.

---
## 5) Operator Definitions
**Operator:** `Glyphser.Environment.BuildManifest`  
**Category:** Environment  
**Signature:** `(() -> env_manifest)`  
**Purity class:** IO  
**Determinism:** deterministic given unchanged runtime facts and capture sources  
**Definition:** Captures required runtime facts, applies normalization, computes constituent hashes, emits schema-valid manifest.

**Operator:** `Glyphser.Environment.ComputeManifestHash`  
**Category:** Environment  
**Signature:** `(env_manifest -> env_manifest_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Computes `SHA-256(CBOR_CANONICAL(env_manifest))`.

**Operator:** `Glyphser.Environment.ValidateCompatibility`  
**Category:** Environment  
**Signature:** `(candidate_manifest, required_manifest? -> compatibility_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Validates compatibility using complete-manifest semantics:
- `required_manifest`, when provided, is the full required schema (section 2.6),
- if `required_manifest` is absent, compatibility is not evaluated and report status is `NOT_CHECKED`,
- compatibility holds iff every required field exists in `candidate_manifest` and equals the corresponding required value,
- extra fields in `candidate_manifest` are ignored for compatibility but violate schema-lint if candidate is validated as canonical manifest,
- `missing_fields` = count of required fields absent in candidate,
- `compatibility_failures` = number of unequal required fields and MUST equal `len(mismatches)`.
- CBOR equality semantics: field equality uses byte-identical canonical CBOR values (`null` is only equal to `null`).
- precondition: if `required_manifest` is provided it MUST be schema-valid per section 2.6; otherwise abort with `CONTRACT_VIOLATION`.

**`compatibility_report` minimum schema (canonical CBOR map):**
- `is_compatible:bool`
- `candidate_hash:bytes32`
- `required_hash?:bytes32` (present iff `required_manifest` is provided)
- `mismatches:array<{path:string, candidate_value:string, required_value:string}>` sorted by `path` bytewise
  - canonical value-to-string rendering:
    - `bytes32` -> lowercase hex (64 chars, no `0x`),
    - `null` -> literal `__NULL__`,
    - text string -> exact UTF-8 string.
- `missing_fields:uint64`
- `compatibility_failures:uint64`
- `compatibility_status:enum("COMPATIBLE","INCOMPATIBLE","NOT_CHECKED")`
- `is_compatible` is true iff `missing_fields==0` and `compatibility_failures==0` and `compatibility_status=="COMPATIBLE"`.

---
## 6) Procedure
```text
1. BuildManifest
2. ComputeManifestHash
3. ValidateCompatibility (against required baseline, if provided)
4. Return env_manifest + env_manifest_hash + compatibility_report
```

---
## 7) Trace & Metrics
### 6.1 Logging Rule
- Environment capture/validation emits deterministic records.
- Trace emission mapping:
  - `BuildManifest`: emits capture `iter` events and run-level capture status.
  - `ValidateCompatibility`: emits compatibility `iter` events and final compatibility status.
- On field capture/normalization/hash failure, emit `iter` with `status=\"ERROR\"` for the affected top-level field path before abort.

### 6.2 Trace Schema
- `run_header`: `{schema_version:string}`
- `iter`: `{field_path:string, status:enum("CAPTURED","MISSING","MISMATCH","ERROR")}`
- `run_end`: `{env_manifest_hash:bytes32, compatibility_status:enum("COMPATIBLE","INCOMPATIBLE","NOT_CHECKED")}`
- validation event mapping:
  - missing required field in candidate -> `iter(status=\"MISSING\")`,
  - present but unequal -> `iter(status=\"MISMATCH\")`,
  - malformed manifest or validation fault -> `iter(status=\"ERROR\")` then abort,
  - matching fields may omit `iter` event.
- iter ordering rule:
  - `iter` events MUST follow ascending bytewise order of manifest field keys (same order as canonical CBOR map keys).

### 6.3 Metric Schema
- `missing_fields` produced by `BuildManifest` and `ValidateCompatibility`; MUST be emitted when detected, including error-before-abort cases.
- `compatibility_failures` produced by `ValidateCompatibility`.

### 6.4 Comparability Guarantee
- Comparable iff `schema_version` matches and canonical CBOR profile is identical.

---
## 8) Validation
### 7.1 Lint Rules (mandatory)
- Manifest map contains exactly required fields (no extras, no missing).
- `schema_version` equals `Glyphser.Environment.Manifest`.
- All hash fields are `bytes32` encoded as CBOR byte strings (major type 2) of exactly 32 bytes.
- Canonical CBOR encoding used for all commitments.

### 7.2 Operator Test Vectors (mandatory)
- Fixed capture inputs/snapshots produce fixed `env_manifest_hash`.
- Compatibility fixtures for match/mismatch cases.

### 7.3 Golden Traces (mandatory)
- Golden capture and compatibility traces with fixed hashes.

---
## 9) Refactor & Equivalence
### 8.1 Equivalence Levels
- `E0` required for manifest bytes, `env_manifest_hash`, and compatibility verdict/report.

### 8.2 Allowed Refactor Categories
- Capture implementation changes that preserve normalized field values and final manifest bytes/hash.

### 8.3 Equivalence Test Procedure (mandatory)
- Canonical-byte compare of manifest maps.
- Exact compare of `env_manifest_hash` and `compatibility_report`.

---
## 10) Checkpoint/Restore
### 9.1 Checkpoint Contents
- `env_manifest_hash:bytes32`
- `schema_version:string`

### 9.2 Serialization
- Deterministic canonical CBOR.

### 9.3 Restore Semantics
- Restore retrieves manifest by `env_manifest_hash` from content-addressable storage.
- Restored run MUST match committed `env_manifest_hash`; otherwise abort deterministically.
- Content-addressable storage mechanism is out of scope, but exact original manifest bytes MUST be retrievable by hash.

---
## 11) EQC Alignment Notes
- This document preserves EQC block structure with domain-specific mappings:
  - Block V observability semantics are represented in section `6) Trace & Metrics`.
  - Block VI parallel/nondeterminism semantics are represented in section `0.E` and relevant deterministic ordering rules.
  - Block IX checkpoint/restore semantics are represented in section `9) Checkpoint/Restore`.
