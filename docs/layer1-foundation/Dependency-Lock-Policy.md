# Glyphser Dependency Lock Policy
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.DependencyLockPolicy`
**Purpose (1 sentence):** Define deterministic dependency pinning, lock validation, artifact integrity verification, and upgrade-governance semantics for reproducible builds and runs.
**Spec Version:** `Glyphser.Implementation.DependencyLockPolicy` | 2026-02-19 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Build/runtime dependency control.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.DependencyLockPolicy`
- **Purpose (1 sentence):** Deterministic dependency governance.
- **Spec Version:** `Glyphser.Implementation.DependencyLockPolicy` | 2026-02-19 | Authors: Olejar Damir
- **Domain / Problem Class:** Reproducible dependency management.

### 0.A Objective Semantics
- This contract performs deterministic validation and policy evaluation; it is not an optimization algorithm.
- Diagnostic primary metric tuple: `(hash_mismatches:uint64, policy_violations:uint64)`.
- Primary comparison rule: exact lock/schema/policy conformance and exact digest equality.

### 0.B Reproducibility Contract
- Replayable given `(lockfile_blob, policy_blob, artifact_index_blob, sbom_hash, toolchain_hash, runtime_env_hash)`.
- `toolchain_hash` and `runtime_env_hash` are replay inputs.
- `dependencies_lock_hash` is derived output: `SHA-256(CBOR_CANONICAL(["deps_lock", [lockfile_hash, toolchain_hash, runtime_env_hash, sbom_hash]]))`.
- Artifact verification replay requires content-addressed immutable artifact retrieval from `artifact_index_blob` locations; this store assumption is part of runtime environment reproducibility (anchored by `runtime_env_hash`).

### 0.C Numeric Policy
- This section also defines deterministic version-comparison behavior for dependency governance.
- Semantic version parsing MUST follow SemVer 2.0.0 for valid SemVer strings.
- Non-SemVer version strings MUST be compared as raw UTF-8 strings in bytewise lexicographic order.
- Upgrade-comparison mixed-scheme rule: if one side is SemVer and the other is non-SemVer, the change is invalid (`VERSION_SCHEME_MISMATCH`) unless a future policy version explicitly permits mixed-scheme comparison.

### 0.D Ordering and Tie-Break Policy
- Unless explicitly overridden, all string ordering uses ascending bytewise UTF-8 lexicographic order.
- Lock tuples are sorted by `(name, version, source)`.
- Deterministic report ordering is mandatory for all emitted arrays (defined per schema below).

### 0.E Parallel, Concurrency, and Reduction Policy
- Validation and artifact checks MAY run in parallel.
- Parallel merge rule:
  - overall validity = logical-AND of all partial validity flags,
  - partial lists are concatenated and then globally sorted by their normative order keys before emission,
  - trace `iter` records MUST be emitted in global sorted package/check order independent of execution scheduling.

### 0.F Environment and Dependency Policy
- Determinism target for contract-critical outputs (`lock_verdict`, `dependencies_lock_hash`, trace commitments) is `E0`.

### 0.G Operator Manifest
- `Glyphser.DepLock.ValidateLockfile`
- `Glyphser.DepLock.VerifyArtifactHashes`
- `Glyphser.DepLock.EvaluateUpgradeRequest`
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- Operators are fully-qualified and versioned.
- Canonical lock-policy location: `contracts/dependency_lock_policy.cbor`.

### 0.I Outputs and Metric Schema
- Outputs: `(lock_verdict, upgrade_report?)`.
- `lock_verdict` schema:
  - `is_valid_lock:bool`
  - `is_artifact_integrity_valid:bool`
  - `lockfile_hash:bytes32`
  - `dependencies_lock_hash:bytes32`
  - `policy_bundle_hash:bytes32`
  - `validation_report:LockValidationReport`
  - `verification_report:ArtifactVerificationReport`
- Metric schema:
  - `packages_total:uint64`
  - `hash_mismatches:uint64`
  - `policy_violations:uint64`

### 0.J Spec Lifecycle Governance
- Any normative schema/rule/ordering change requires version bump and migration notes.
- Policy version MUST be included in `policy_bundle_hash` input.

### 0.K Failure and Error Semantics
- Deterministic abort conditions:
  - malformed lockfile (`LOCKFILE_PARSE_ERROR`),
  - malformed policy (`POLICY_SCHEMA_ERROR`),
  - malformed artifact index (`ARTIFACT_INDEX_SCHEMA_ERROR`),
  - forbidden dependency source (`FORBIDDEN_SOURCE`),
  - unresolved required artifact (`ARTIFACT_MISSING`),
  - digest mismatch (`ARTIFACT_HASH_MISMATCH`),
  - missing required toolchain/runtime inputs (`INPUT_MISSING`),
  - checkpoint lockfile mismatch on restore (`LOCKFILE_MISMATCH`),
  - checkpoint policy mismatch on restore (`POLICY_BUNDLE_MISMATCH`),
  - checkpoint artifact-index mismatch on restore (`ARTIFACT_INDEX_MISMATCH`),
  - checkpoint SBOM mismatch on restore (`SBOM_HASH_MISMATCH`),
  - checkpoint toolchain hash mismatch on restore (`TOOLCHAIN_HASH_MISMATCH`),
  - checkpoint runtime environment hash mismatch on restore (`RUNTIME_ENV_HASH_MISMATCH`).
- On abort, emit `Glyphser.Error.Emit` with deterministic `CONTRACT_VIOLATION` payload containing one canonical code above and stop.

### 0.L Input/Data Provenance
- Lockfile source and artifact provenance are mandatory.
- Policy and artifact index blobs MUST be content-addressable and hash-pinned.

---
### 0.Z EQC Mandatory Declarations Addendum
- Contract class: deterministic; stochastic declarations are N/A.
- Floating-point tolerance declarations are N/A for critical verdict computation.
- Error trace rule: final failure record includes `step_index:uint64`, `failure_code`, `failure_operator`, and minimal deterministic diagnostics.
- `step_index` is the 0-based index of the failed step in Section 6 Procedure (step 1 -> index 0, ..., step 8 -> index 7).
- Recovery policy: deterministic abort-only unless explicitly declared by a future version.

---
## 2) System Model
### I.A Persistent State
- Approved lock policy registry.
- Approved artifact index schema version.

### I.B Inputs and Hyperparameters
- `lockfile_blob:bytes`
- `policy_blob:bytes`
- `artifact_index_blob:bytes`
- `sbom_hash:bytes32`
- `toolchain_hash:bytes32`
- `runtime_env_hash:bytes32`
- `upgrade_proposal_blob?:bytes`
- `strict_mode:bool` (from policy; MUST be explicit)

### I.C Constraints and Feasible Set
A run is feasible iff all of the following hold:
- lockfile parses under one supported format with canonical extraction rules,
- policy schema validates,
- artifact index schema validates,
- all required package entries are pinned and policy-compliant,
- all required artifacts are hash-verifiable,
- required external inputs (`sbom_hash`, `toolchain_hash`, `runtime_env_hash`) are provided.

### I.D Transient Variables
- `normalized_lock_entries:array<LockTuple>`
- `violations:array<Violation>`
- `mismatches:array<HashMismatch>`

### I.E Invariants and Assertions
- In strict mode, unlocked transitive dependencies are forbidden.
- Every resolved dependency in lock scope has exactly one normalized tuple.
- Every tuple in lock scope has exactly one effective integrity policy outcome.
- For any given `(name, source)` combination, there is at most one normalized tuple.

### II.F Normative Data Schemas
- Canonical serialization for all typed objects in this contract is canonical CBOR per `docs/layer1-foundation/Canonical-CBOR-Profile.md` and RFC 8949 deterministic encoding rules.

`LockTuple`:
- `name:tstr` (non-empty)
- `version:tstr` (non-empty)
- `source:tstr`
- `integrity_hash:bytes32`

`Policy` (exact fields; no extras):
- `policy_version:uint32` (>=1)
- `strict_mode:bool`
- `allowed_sources:array<tstr>` (sorted unique)
- `allow_direct_url_dependencies:bool` (MUST be `false` in v1)
- `allow_source_changes:bool` (MUST be `false` in v1)
- `allowed_upgrade_scopes:array<enum("patch","minor","major")>` (sorted unique)
- `gpu_runtime_pinning_required:bool`
- `determinism_env_var_allowlist:array<tstr>` (sorted unique)

`ArtifactIndex` (exact fields; no extras):
- `index_version:uint32` (>=1)
- `artifacts:array<ArtifactRecord>`

`ArtifactRecord` (exact fields; no extras):
- `name:tstr`
- `version:tstr`
- `source:tstr`
- `artifact_sha256:bytes32`
- `location:tstr` where `location` MUST be content-addressed (`sha256:<64-hex>` or equivalent content-addressed immutable URI). Non-content-addressed filesystem paths are forbidden in v1.
- runtime requirement: for identical `runtime_env_hash`, content-addressed `location` resolution MUST yield identical bytes.

`UpgradeProposal` (exact fields; no extras):
- `proposal_version:uint32` (>=1)
- `changes:array<UpgradeChange>`

`UpgradeChange`:
- `name:tstr`
- `from_version:tstr`
- `to_version:tstr`
- `source:tstr`

### II.G External Definitions Bound by Reference
- `runtime_env_hash` is the canonical environment commitment (`env_manifest_hash`) from `docs/layer1-foundation/Environment-Manifest.md`.
- Error payload structure and canonical codes are defined in `docs/layer1-foundation/Error-Codes.md`.
- `gpu_runtime_pinning_required` and `determinism_env_var_allowlist` are consumed by environment/deployment validation contracts; this lock-policy contract does not validate live GPU runtime state.

### II.H Normative Hashes and Canonicalization
`toolchain_hash`:
- Input is `toolchain_hash:bytes32` provided by caller.
- `toolchain_hash` is opaque for this contract; production/validation rules are defined by the producer contract that emits it.

`source` canonicalization (normative):
- Normalize source strings before tuple emission:
  - apply Unicode NFC normalization,
  - lowercase scheme and host components when URL-like,
  - `pypi`, `pypi.org`, `pypi.python.org`, `https://pypi.org`, `http://pypi.org/simple`, `https://pypi.org/simple/` map to `https://pypi.org/simple`,
  - if no mapping exists, keep source string unchanged after NFC normalization.
- `allowed_sources` comparison uses the canonicalized source string only.

`LockfileDigest`:
- Parse lockfile into `LockTuple` entries using format-specific canonical rules:
  - `requirements.txt` with hashes:
    - comments MUST be whole-line comments only (first non-whitespace char is `#`); inline comments on requirement lines are invalid in v1,
    - trim whitespace, ignore empty/comment lines,
    - `--index-url` directives MUST appear on their own lines,
    - line continuations (trailing `\\`) are forbidden in v1 and make the lockfile invalid,
    - `--extra-index-url` and `--find-links` directives are forbidden in v1 and make the lockfile invalid,
    - editable installs (`-e`) and include directives (`-r`) are forbidden in v1 and make the lockfile invalid,
    - environment markers (`;` outside quoted strings) are forbidden in v1 and make the lockfile invalid,
    - source context is cumulative top-to-bottom: each `--index-url` directive applies to all subsequent requirement lines until overridden by a later `--index-url`,
    - process effective requirement lines containing `--hash=sha256:<hex>`,
    - extract package name as token before first version comparator (`==`, `>=`, `<=`, `~=`, `!=`, `<`, `>`),
    - strip extras suffix from package token (remove `[...]` and everything after `[`),
    - extract pinned version only when `==` is present; otherwise line is invalid in v1 strict lock mode,
    - source for a requirement line is the most recent prior in-file `--index-url`; if none, canonical PyPI source,
    - integrity hash is the first `sha256` hash token on the line.
    - hash token decoding rule (applies to all formats): token MUST match `sha256:<64-hex>` (case-insensitive `sha256` prefix, hex tail length exactly 64). Decode hex tail to `bytes32`; otherwise lockfile is invalid.
  - `poetry.lock`:
    - traverse `[[package]]` entries,
    - extract `name` and `version`,
    - source comes from package source URL if present else canonical PyPI source,
    - sort package file entries by `file` (bytewise UTF-8) then use the first available `sha256` token and decode per hash token decoding rule above; missing/invalid hash is invalid in v1 strict lock mode.
  - `uv.lock`:
    - traverse locked package records,
    - extract `name`, `version`, source/index URL (or canonical PyPI default),
    - integrity hash token is required and decoded per hash token decoding rule above; missing/invalid hash is invalid in v1 strict lock mode.
- Environment markers and extras policy (v1): include all locked entries exactly as lockfile declares; marker-conditioned activation is out of scope for this contract.
- Artifact-index coverage rule for markers/extras: artifact index MUST include entries for all lockfile tuples, including marker-conditioned entries.
- Sort tuples by `(name, version, source)` using bytewise UTF-8 lexicographic order.
- `lockfile_hash = SHA-256(CBOR_CANONICAL(sorted_lock_tuples))`.

`DependenciesLockDigest`:
- `dependencies_lock_hash = SHA-256(CBOR_CANONICAL(["deps_lock", [lockfile_hash, toolchain_hash, runtime_env_hash, sbom_hash]]))`.

`policy_bundle_hash`:
- `policy_bundle_hash = SHA-256(CBOR_CANONICAL(["policy_bundle", [policy_version, policy_blob]]))`.

`artifact_index_hash`:
- `artifact_index_hash = SHA-256(CBOR_CANONICAL(artifact_index_blob))`.

### II.I Policy Rules
- Accepted lockfile formats:
  - `poetry.lock`
  - `requirements.txt` with required hash pins
  - `uv.lock`
- Registry/source rule:
  - dependency source MUST be in `allowed_sources`.
  - direct URL dependency definition (v1): any dependency source not equal to a canonical registry source string in `allowed_sources` is a direct URL dependency and is forbidden (`allow_direct_url_dependencies` MUST be false).
- SBOM rule:
  - `sbom_hash` MUST be provided as input and included in trace `run_header`.
  - `sbom_hash` contributes to `dependencies_lock_hash`; therefore it is part of reproducible verdict commitments, not trace-only metadata.
- GPU/runtime pinning note:
  - this contract carries policy fields but does not enforce runtime hardware/driver state.

---
## 3) Initialization
1. Decode and validate `policy_blob` and `artifact_index_blob` schemas.
2. Parse `lockfile_blob` into normalized `LockTuple` entries.
3. Build deterministic verification context (sorted tuples, source allowlist set, artifact lookup map).

---
## 4) Operator Manifest
- `Glyphser.DepLock.ValidateLockfile`
- `Glyphser.DepLock.VerifyArtifactHashes`
- `Glyphser.DepLock.EvaluateUpgradeRequest`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md`.

`LockValidationReport`:
- `is_valid:bool`
- `violations:array<Violation>` sorted by `(path, code)`

`Violation`:
- `path:tstr`
- `code:enum("LOCKFILE_PARSE_ERROR","POLICY_SCHEMA_ERROR","ARTIFACT_INDEX_SCHEMA_ERROR","FORBIDDEN_SOURCE","UNPINNED_DEPENDENCY","STRICT_MODE_VIOLATION","INPUT_MISSING","LOCKFILE_MISMATCH","POLICY_BUNDLE_MISMATCH","ARTIFACT_INDEX_MISMATCH","SBOM_HASH_MISMATCH","TOOLCHAIN_HASH_MISMATCH","RUNTIME_ENV_HASH_MISMATCH","VERSION_SCHEME_MISMATCH","PACKAGE_NOT_FOUND","PROPOSAL_VERSION_MISMATCH","EMPTY_VERSION","POLICY_CONTRACT_ERROR")`
- `message:tstr`
- `path` semantics:
  - package-specific violation: `path` is package name,
  - global violation: `path` is `GLOBAL`.

`ArtifactVerificationReport`:
- `is_valid:bool`
- `hash_mismatches:array<HashMismatch>` sorted by `(name, version, source)`
- `missing_artifacts:array<tstr>` sorted ascending
- each `missing_artifacts` entry MUST be `name + " " + version + " " + source`.

`HashMismatch`:
- `name:tstr`
- `version:tstr`
- `source:tstr`
- `expected_hash:bytes32`
- `observed_hash:bytes32`

`UpgradeReport`:
- `is_allowed:bool`
- `risk_class:enum("LOW","MEDIUM","HIGH","CRITICAL")`
- `disallowed_changes:array<UpgradeChange>` sorted by `(name, from_version, to_version, source)`
- `notes:array<tstr>` sorted ascending

**Operator:** `Glyphser.DepLock.ValidateLockfile`
- **Category:** IO
- **Signature:** `(lockfile_blob:bytes, policy_blob:bytes -> lock_validation_report:LockValidationReport, lockfile_hash:bytes32, policy_bundle_hash:bytes32)`
- **Purity class:** PURE
- **Determinism:** deterministic
- **Definition:**
  - Validates policy schema before computing `policy_bundle_hash`.
  - Parses and normalizes lock entries.
  - Validates source allowlist and strict-mode invariants.
  - Validates required pins and policy constraints.
  - Returns deterministic sorted violations.

**Operator:** `Glyphser.DepLock.VerifyArtifactHashes`
- **Category:** IO
- **Signature:** `(lockfile_blob:bytes, artifact_index_blob:bytes -> artifact_verification_report:ArtifactVerificationReport)`
- **Purity class:** IO
- **Determinism:** deterministic given immutable content-addressed artifact retrieval
- **Definition:**
  - Resolves each lock tuple against artifact index record by `(name, version, source)`.
  - Retrieves artifact bytes via immutable content-addressed `location`.
  - Computes SHA-256 over artifact bytes as `observed_hash`.
  - Sets `expected_hash` to the lock tuple `integrity_hash`.
  - If `observed_hash != expected_hash`, records a hash mismatch.
  - If artifact retrieval fails, records a missing artifact.
  - Records missing artifacts and mismatches deterministically.

**Operator:** `Glyphser.DepLock.EvaluateUpgradeRequest`
- **Category:** IO
- **Signature:** `(current_lockfile_blob:bytes, proposal_blob:bytes, policy_blob:bytes -> upgrade_report:UpgradeReport)`
- **Purity class:** PURE
- **Determinism:** deterministic
- **Definition:**
  - Parses proposal changes.
  - If `changes` is empty, return `is_allowed=true`, `risk_class=LOW`, and empty `disallowed_changes`/`notes`.
  - Reject duplicate proposal changes by `(name, from_version, to_version, source)`.
  - Canonicalize each change `source` using the source canonicalization rules in Section II.H before comparisons.
  - For each change, find lock tuple by exact `(name, source)` match in current lock using canonicalized `source`.
  - If no tuple with matching `(name, source)` exists, change is disallowed (`PACKAGE_NOT_FOUND`).
  - If `from_version` or `to_version` is empty, change is disallowed (`EMPTY_VERSION`).
  - The matched tuple version MUST equal `from_version`; otherwise disallowed (`PROPOSAL_VERSION_MISMATCH`).
  - `UpgradeProposal` in v1 is delta-only for existing packages; additions/removals are out of scope and therefore disallowed.
  - If exactly one of `from_version` or `to_version` is valid SemVer 2.0.0, change is disallowed (`VERSION_SCHEME_MISMATCH`).
  - Source-change rule:
    - if `source` differs from current source and `allow_source_changes=false`, change is disallowed,
    - if `allow_source_changes=true`, new source MUST be in `allowed_sources`; otherwise disallowed.
  - Downgrade/no-op rule:
    - if `to_version == from_version` and source unchanged, change is a no-op and allowed,
    - if `to_version < from_version` according to version comparison policy in `0.C`, change is disallowed in v1.
  - SemVer pre-release/build metadata uses SemVer 2.0.0 precedence.
  - SemVer scope classification (when both versions are valid SemVer):
    - compare version core `(major.minor.patch)` ignoring pre-release/build metadata,
    - major differs -> `major`,
    - else minor differs -> `minor`,
    - else patch differs -> `patch`,
    - else same core with metadata-only change -> `patch`.
  - If both versions are non-SemVer, classify as `non_semver`.
  - Because policy `allowed_upgrade_scopes` excludes `non_semver` in v1, any `non_semver` change is automatically disallowed.
  - Applies `allowed_upgrade_scopes` policy.
  - Risk is the highest scope among all allowed changes with ranking `patch < minor < major = non_semver`; if any disallowed change exists, `risk_class = CRITICAL`.

---
## 6) Procedure
1. Run `ValidateLockfile`.
2. If `lock_validation_report.is_valid=false`, emit deterministic `CONTRACT_VIOLATION` and abort.
3. Run `VerifyArtifactHashes`.
4. If `artifact_verification_report.is_valid=false`, emit deterministic `CONTRACT_VIOLATION` and abort.
5. Form `dependencies_lock_hash` from `lockfile_hash` and provided inputs `toolchain_hash`, `runtime_env_hash`, and `sbom_hash`.
6. Include provided `sbom_hash` in trace commitments and dependency-lock commitment calculation.
7. Optionally run `EvaluateUpgradeRequest` when proposal is provided.
8. Emit `lock_verdict` and optional `upgrade_report`.

---
## 7) Trace & Metrics
### Logging rule
- Every verification run emits deterministic trace records encoded in canonical CBOR.

### Trace schema
- `run_header`:
  - `lockfile_hash:bytes32`
  - `policy_bundle_hash:bytes32`
  - `artifact_index_hash:bytes32`
  - `sbom_hash:bytes32`
- `iter`:
  - `package_name:tstr`
  - `package_version:tstr`
  - `source:tstr`
  - `check:enum("SOURCE_POLICY","LOCK_PIN","ARTIFACT_HASH")`
  - `result:enum("PASS","FAIL")`
- `run_end`:
  - `status:enum("PASS","FAIL")`
  - `mismatch_summary:map{hash_mismatches:uint64, policy_violations:uint64, missing_artifacts:uint64}`

### Deterministic iter completeness
- For each package in sorted lock tuple order, always emit all three checks in fixed order `SOURCE_POLICY`, `LOCK_PIN`, `ARTIFACT_HASH`.
- `LOCK_PIN` definition: validate that the tuple has an integrity hash (`integrity_hash:bytes32`) compliant with v1 lock requirements; absence, malformed hash, or all-zero 32-byte hash yields `FAIL`.
- `ARTIFACT_HASH` definition:
  - `PASS` if artifact exists in index/store and computed SHA-256 equals expected hash,
  - `FAIL` if artifact exists but digest mismatches, or artifact is missing.

### Metric schema
- `packages_total:uint64`
- `hash_mismatches:uint64`
- `policy_violations:uint64`

### Comparability guarantee
- Full-output comparability (including `dependencies_lock_hash`) requires bytewise-identical `lockfile_hash`, `policy_bundle_hash`, `artifact_index_hash`, `toolchain_hash`, `runtime_env_hash`, and `sbom_hash`.
- Validation-only comparability (excluding derived commitment fields) requires bytewise-identical `lockfile_hash`, `policy_bundle_hash`, and `artifact_index_hash`.

---
## 8) Validation
### VII.A Lint rules (mandatory)
- Reject unknown fields in `Policy`, `ArtifactIndex`, and `UpgradeProposal`.
- Reject duplicate lock tuples by `(name, version, source)`.
- Reject multiple lock tuples with the same `(name, source)` combination.
- Reject unsorted/duplicate `allowed_sources` and `allowed_upgrade_scopes`.
- Reject duplicate `UpgradeProposal.changes` by `(name, from_version, to_version, source)`.
- Reject multiple `UpgradeProposal.changes` entries with the same `(name, source)` combination.
- Reject duplicate `ArtifactRecord` entries by `(name, version, source)`.
- Reject `requirements.txt` inline comments on requirement lines and reject `--index-url` directives not on standalone lines.
- Reject `requirements.txt` line continuations (trailing `\\`).
- Reject `requirements.txt` directives `--extra-index-url` and `--find-links`.
- Reject `requirements.txt` editable installs (`-e`) and include directives (`-r`).
- Reject `requirements.txt` environment markers (`;` outside quoted strings).
- Reject any direct URL dependencies in v1.

### VII.B Operator test vectors (mandatory)
- Valid lockfile + valid index (pass).
- Forbidden source (fail).
- Hash mismatch (fail).
- Missing artifact (fail).
- Allowed patch upgrade (allow).
- Disallowed downgrade (critical).
- Disallowed major upgrade under patch/minor-only policy (critical).

### VII.C Golden traces (mandatory)
- Golden trace sets for canonical lockfiles, including `run_header` commitments and deterministic `run_end` summaries.

---
## 9) Refactor & Equivalence
### VIII.A Equivalence levels
- `E0` applies to lock verdict, dependencies lock hash, and deterministic trace commitment fields.

### VIII.B Allowed refactor categories
- Internal parser/verifier optimization preserving all normative outputs and ordering.

### VIII.C Equivalence test procedure (mandatory)
- Exact comparison of `lock_verdict` and commitment hashes over baseline lockfiles.
- For trace equivalence, exact compare of `run_header`, `iter`, and `run_end` for same input set.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- `verification_cursor:uint64` (next tuple index to process in sorted lock tuple array; initial value `0`)
- `partial_hash_mismatches:array<HashMismatch>` (sorted)
- `partial_policy_violations:array<Violation>` (sorted)
- `lockfile_hash:bytes32`
- `policy_bundle_hash:bytes32`
- `artifact_index_hash:bytes32`
- `sbom_hash:bytes32`
- `toolchain_hash:bytes32`
- `runtime_env_hash:bytes32`

### Serialization
- Canonical CBOR.

### Restore semantics
- Restore requires re-supplying the same `lockfile_blob`; parsing MUST reproduce identical sorted tuples and `lockfile_hash`.
- On restore, recompute `lockfile_hash` from supplied lockfile and compare to checkpoint `lockfile_hash`; mismatch MUST abort with `LOCKFILE_MISMATCH`.
- Because `lockfile_hash` matches and parsing is deterministic, the sorted tuple list is identical to the original list and resumption order is preserved.
- Restore requires re-supplying `policy_blob`, `artifact_index_blob`, and `sbom_hash`.
- Recompute and compare `policy_bundle_hash` and `artifact_index_hash` against checkpoint values; mismatches MUST abort with `POLICY_BUNDLE_MISMATCH` or `ARTIFACT_INDEX_MISMATCH`.
- Supplied `sbom_hash` MUST equal checkpoint `sbom_hash`; mismatch MUST abort with `SBOM_HASH_MISMATCH`.
- Restore requires re-supplying `toolchain_hash` and `runtime_env_hash`.
- Supplied `toolchain_hash` and `runtime_env_hash` MUST equal checkpoint values; mismatches MUST abort with `TOOLCHAIN_HASH_MISMATCH` or `RUNTIME_ENV_HASH_MISMATCH`.
- Checkpointing MUST occur only at tuple boundaries after all checks for a tuple are complete.
- Restore resumes from `verification_cursor` in the same sorted tuple order.
- Restored run MUST produce byte-identical final reports and verdict as uninterrupted execution.
