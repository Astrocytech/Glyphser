# Glyphser Config Schema Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Config.SchemaValidator`  
**Purpose (1 sentence):** Define and validate the canonical manifest/config schema used by all Glyphser components.  
**Spec Version:** `Glyphser.Config.SchemaValidator` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Deterministic configuration validation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Config.SchemaValidator`
- **Purpose (1 sentence):** Canonical manifest schema enforcement.
- **Spec Version:** `Glyphser.Config.SchemaValidator` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Config schema validation.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize schema violations.
### 0.B Reproducibility Contract
- Replayable given `(schema_version, manifest_hash)`.
### 0.C Numeric Policy
- Type/constraint checks deterministic; float constraints in binary64.
### 0.D Ordering and Tie-Break Policy
- Field validation order is canonical by schema key path.
### 0.E Parallel, Concurrency, and Reduction Policy
- Validation is deterministic single-pass.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for validation output.
### 0.G Operator Manifest
- `Glyphser.Config.ValidateRequiredFields`
- `Glyphser.Config.ValidateTypes`
- `Glyphser.Config.ValidateRanges`
- `Glyphser.Config.NormalizeDefaults`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Fully-qualified config operators required.
### 0.I Outputs and Metric Schema
- Outputs: `(normalized_manifest, validation_report)`.
- Metrics: `missing_fields`, `type_errors`, `range_errors`.
- Completion status: `success | failed`.
### 0.J Spec Lifecycle Governance
- Breaking schema changes require MAJOR bump.
### 0.K Failure and Error Semantics
- Abort-only on invalid manifest.
### 0.L Input/Data Provenance
- Input manifest hash and source path recorded.

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
- schema registry.
### I.B Inputs and Hyperparameters
- raw manifest and schema version.
### I.C Constraints and Feasible Set
- Valid if all required/type/range checks pass.
### I.D Transient Variables
- validation diagnostics.
### I.E Invariants and Assertions
- normalized manifest is canonical and deterministic.

### II.F Authoritative Manifest Schema (Concrete)
- Canonical serialization: `CBOR_CANONICAL` as defined in `docs/layer1-foundation/Canonical-CBOR-Profile.md`.
- `manifest_hash = SHA-256(canonical_manifest_cbor)`.
- `schema_mode: enum("AUTHORITATIVE","MODULAR")` (default `AUTHORITATIVE`).
- Required top-level fields:
  - `spec_version:string`
  - `tenant_id:string`
  - `seed:uint64`
  - `global_batch_size:uint64 (>=1)`
  - `datasets:object`
  - `environment:object`
  - `pipeline_stages:array<object>`
  - `model:object`
  - `security:object`
  - `optimizer:object`
  - `policy_bundle:object`
  - policy note: `policy.rules` (runtime stage/action control) is distinct from `policy_bundle` (security/authz/monitor commitment hashes); both may coexist.
- Optional top-level fields:
  - `task_type:enum(multiclass|binary|regression)`
  - `alpha:float64` (default `1.0`)
  - `execution_mode:enum(local|managed|confidential|regulated)` (default `managed`)
  - `fingerprint_frequency:uint64` (default `0`)
  - `grad_clip_norm:float64`
  - `checkpoint_frequency:uint64` (default `0`)
  - `job_priority:uint64` (recommended range `1..10`)
  - `policy:object` with optional `rules:array<object>` for runtime stage decisions
  - `data:object` with optional:
    - `sampler_block_size:uint64` (default `1048576`)
    - `drop_last:bool` (default `false`)
  - `custom_operators:array<object>`
  - `parallelism:object` with optional:
    - `strategy:string`
    - `world_size_override:uint64`
    - `sharding_config:object`
  - `manifest_inheritance:object` with optional:
    - `parent_manifest_path:string`
  - `hardware_affinity:object` with optional:
    - `gpu_ids:array<uint64>`
    - `cpu_cores:array<uint64>`
  - `profile:enum(research|enterprise|regulated)`
  - `backend:object` with optional/required subfields:
    - `name:string`
  - `resource_requests:object` with optional:
    - `cpus:uint64`
    - `gpus:uint64`
    - `memory_gb:float64`
  - `memory_arena_config:object` (optional deterministic TMMU arena configuration)
  - `quota:object` with optional:
    - `memory_bytes_budget:uint64`
    - `gpu_time_ms_budget:uint64`
    - `cpu_time_ms_budget:uint64`
    - `io_bytes_budget:uint64`
  - `rbac:object` with optional:
    - `principals:array<object>`
    - `permissions:map`
  - `storage:object` with optional:
    - `backend:string`
    - `endpoint:string`
    - `bucket:string`
    - `credentials_secret:string`
  - `monitoring_export:object` with optional:
    - `prometheus_endpoint:string`
    - `log_sink:string`
  - `rbac_source:enum(local|ldap|oidc)` (default `local`)
  - `daemon_mode:enum(standalone|cluster)` (default `standalone`)
  - `distributed:object` with optional:
    - `timeout_seconds:uint64` (default `300`)
  - `fine_tune:object`
  - `evaluation:object`
  - `compute_dtype:enum(float32|float64)` (default `float32`)
  - `trace:object` with optional:
    - `schema_version:string`
    - `max_bytes_per_step:uint64`
    - `sample_policy:string`
- Required `security.differential_privacy` fields when enabled:
  - `enabled:bool`, `accountant:string`, `target_epsilon:float64`, `target_delta:float64`, `noise_multiplier:float64`.
- Required `pipeline_stages[i]` fields:
  - `step_id:string`, `type:enum(train|eval|infer|augment)`, `depends_on:array<string>`.
- Pipeline-stage validation rules (normative):
  - `step_id` values MUST be unique within the manifest.
  - every `depends_on` entry MUST reference an existing `step_id`.
  - forward-order requirement: each dependency MUST reference a stage declared earlier in the array; otherwise validation fails with deterministic `CONTRACT_VIOLATION`.
- Unknown keys policy:
  - In `AUTHORITATIVE` mode: unknown key paths are fatal (`CONTRACT_VIOLATION`).
  - In `MODULAR` mode: unknown keys allowed only under registered extension roots and only when ownership/version checks in II.G pass.
- Required cross-doc fields:
  - `data.sampler_block_size:uint64` (default `1048576`)
  - `compute_dtype:enum(float32,float64)` (default `float32`)
  - `backend.name:string`
  - `trace.schema_version:string`
  - `policy_bundle.policy_bundle_hash:bytes32`
  - `policy_bundle.security_policy_hash:bytes32`
  - `policy_bundle.authz_policy_hash:bytes32`
  - `policy_bundle.monitor_policy_hash:bytes32`
  - `policy_bundle.dp_policy_hash?:bytes32`
  - `policy_bundle.redaction_policy_hash?:bytes32`
  - `environment.env_manifest_hash:bytes32` (as defined in `docs/layer1-foundation/Environment-Manifest.md`; alias `runtime_env_hash` must resolve identically)

### II.F.2 Kernel Manifest Alignment (Normative)
- To preserve cross-file consistency with `docs/layer2-specs/Glyphser-Kernel-v3.22-OS.md` section `0.Q`, the following top-level manifest fields are recognized by this schema (required/optional as noted):
  - required: `spec_version`, `tenant_id`, `seed`, `execution_mode`, `datasets`, `pipeline_stages`, `model`, `security`, `optimizer`, `environment`, `policy_bundle`.
  - optional: `task_type`, `alpha`, `fingerprint_frequency`, `grad_clip_norm`, `checkpoint_frequency`, `job_priority`, `policy.rules`, `data`, `custom_operators`, `parallelism`, `manifest_inheritance`, `hardware_affinity`, `profile`, `backend`, `resource_requests`, `memory_arena_config`, `quota`, `rbac`, `storage`, `monitoring_export`, `rbac_source`, `daemon_mode`, `distributed`, `fine_tune`, `evaluation`, `compute_dtype`, `trace`.
  - `policy.rules` and `policy_bundle` serve different purposes and MAY coexist: policy rules drive runtime stage/action decisions; `policy_bundle` carries cryptographic policy commitments.
- `environment` object alignment:
  - required field: `env_manifest_hash:bytes32`,
  - optional fields: `requirements_hash:string`, `container_image:string`.

### II.F.1 Policy Bundle Commitment (Normative)
- `policy_bundle_hash = SHA-256(CBOR_CANONICAL(["policy_bundle", [security_policy_hash, authz_policy_hash, monitor_policy_hash, dp_policy_hash?, redaction_policy_hash?]]))`.
- `policy_hash` references in other contracts are aliases of `policy_bundle_hash` and must resolve to the same bytes32 value.
- Presence rule:
  - if `policy_bundle_hash` is present and individual component hashes are also present, they MUST match the `policy_bundle` decomposition exactly;
  - if only `policy_bundle_hash` is present, verifiers treat it as an opaque commitment identifier.

### II.G Extension Registry (Normative)
| ext_id | root_prefix | owner_org | signing_key_id | version_range | conflict_policy |
|---|---|---|---|---|---|
| `core_data` | `data.*` | `Glyphser.Core` | `core-signing-ed25519` | `>=1.0,<2.0` | `FAIL` |
| `core_backend` | `backend.*` | `Glyphser.Core` | `core-signing-ed25519` | `>=1.0,<2.0` | `FAIL` |
| `core_tmmu` | `tmmu.*` | `Glyphser.Core` | `core-signing-ed25519` | `>=1.0,<2.0` | `FAIL` |
| `core_trace` | `trace.*` | `Glyphser.Core` | `core-signing-ed25519` | `>=1.0,<2.0` | `FAIL` |
| `core_security` | `security.*` | `Glyphser.Core` | `core-signing-ed25519` | `>=1.0,<2.0` | `FAIL` |

Normative checks in `MODULAR` mode:
- `schema_extensions[ext_id].owner == manifest.extensions[ext_id].owner`
- `manifest.extensions[ext_id].version` must satisfy `version_range`
- two extensions cannot claim overlapping `root_prefix` (`FAIL`)
- overlap refinement rule:
  - nested prefixes are allowed only when owners are identical; longer (more specific) prefix takes precedence.
  - equal-length overlaps with different owners are fatal (`FAIL`).
- `version_range` is interpreted using SemVer 2.0.0 comparison rules (deterministic parser; prerelease ordering per SemVer spec).
- extension signature validation must use `signing_key_id` resolved from trust-store metadata with validity-window and revocation checks at manifest creation time.

### II.G.1 Extension Registration (Normative)
- Extensions are loaded from a deterministic extension registry snapshot and validated at manifest-check time.
- Runtime mutation of extension registry is out-of-scope for this contract version; registry updates must publish a new signed snapshot hash.

### II.H Field Access Rule (Normative)
- Define `MANIFEST_FIELD_ACCESS_SET`: exact set of manifest key paths referenced by kernel, executor, sampler, DP, checkpoint, trace, backend adapter, and deployment operators.
- CI must compute `MANIFEST_FIELD_ACCESS_SET` from static extraction and compare against schema-declared paths.
- Build fails with `CONTRACT_VIOLATION` if any referenced path is undeclared.
- To support dynamic access paths, each operator contract MUST declare manifest field inputs explicitly in its operator signature/contract metadata; runtime validation enforces declared-access subset relation.

### II.I Canonical Defaults Table (Normative)
| field_path | default |
|---|---|
| `data.sampler_block_size` | `1048576` |
| `data.drop_last` | `false` |
| `trace.schema_version` | `Glyphser.Trace.SidecarSchema` |
| `trace.max_bytes_per_step` | `1048576` |
| `trace.sample_policy` | `HASH_GATED` |
| `security.differential_privacy.accountant_granularity` | `PER_STEP` |
| `backend.determinism_profile_id` | `gpu_determinism` |
| `tracking.store_uri` | `cas://tracking/default` |
| `tracking.retention_days` | `90` |
| `security.trust_mode` | `SOFTWARE_ONLY` |

### II.J Deterministic Migration Framework (Normative)
- Manifest schema versions must declare:
  - `schema_version`,
  - `migration_supported_from`,
  - `migration_operator` (for manifests: `Glyphser.Config.ManifestMigrate`).
- Migration output must be deterministic and hash-identical across conforming implementations.
- Each migration run must emit a migration certificate binding:
  - `source_manifest_hash -> target_manifest_hash`,
  - `from_version`, `to_version`, and `migration_policy_hash`.

---
## 3) Initialization
1. Load schema.
2. Parse raw manifest.
3. Initialize diagnostics.

---
## 4) Operator Manifest
- `Glyphser.Config.ValidateRequiredFields`
- `Glyphser.Config.ValidateTypes`
- `Glyphser.Config.ValidateRanges`
- `Glyphser.Config.NormalizeDefaults`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `Glyphser.Config.ValidateRequiredFields`  
**Category:** IO  
**Signature:** `(manifest, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks required keys and nested objects, including pipeline structural constraints:
  - unique `pipeline_stages[].step_id`,
  - every `depends_on` reference exists,
  - each dependency references an earlier stage index.

**Operator:** `Glyphser.Config.ValidateTypes`  
**Category:** IO  
**Signature:** `(manifest, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks scalar/object/list types.

**Operator:** `Glyphser.Config.ValidateRanges`  
**Category:** IO  
**Signature:** `(manifest, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks numeric ranges/enums.

**Operator:** `Glyphser.Config.NormalizeDefaults`  
**Category:** IO  
**Signature:** `(manifest, schema -> normalized_manifest)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** fills defaults and produces canonical ordering.

**Operator:** `Glyphser.Config.ManifestMigrate`
**Category:** IO
**Signature:** `(manifest, from_version, to_version -> migrated_manifest)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** migrates manifest schema deterministically between declared compatible versions while preserving logical semantics.

---
## 6) Procedure
```text
1. ValidateRequiredFields
2. ValidateTypes
3. ValidateRanges
4. NormalizeDefaults
5. Return normalized manifest + report
```

---
## 7) Trace & Metrics
### Logging rule
Validation emits deterministic field-level diagnostics.
### Trace schema
- `run_header`: schema_version, manifest_hash
- `iter`: field_path, check, result
- `run_end`: status
### Metric schema
- `missing_fields`, `type_errors`, `range_errors`
### Comparability guarantee
Comparable iff schema version and canonicalization rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes deterministic field ordering and completeness checks.
#### VII.B Operator test vectors (mandatory)
Includes valid/invalid manifest fixtures.
#### VII.C Golden traces (mandatory)
Golden normalized-manifest hashes and diagnostics.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for normalized manifest and report.
#### VIII.B Allowed refactor categories
- parser/validator optimization preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
Exact diff on normalized manifest/report.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- schema and partial diagnostics.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resume yields identical validation output.

---
## 11) Product Profile Packaging Addendum (Normative)
- In addition to `execution_mode`, deployments MUST support profile packaging IDs:
  - `core`, `enterprise`, `regulated`.
- Profile packaging intent:
  - `core`: minimal, week-one adoption path (single-node default, one backend adapter, one artifact-store adapter, default trace policy).
  - `enterprise`: production operations profile with deployment/runbook and full gate policy.
  - `regulated`: enterprise profile + security/compliance and audit-proof requirements.
- Runtime-mode mapping note:
  - `enterprise` packaging commonly targets `execution_mode=managed`.
- Profile bundle identity:
  - `profile_bundle_hash = SHA-256(CBOR_CANONICAL(profile_bundle))`.
- Promotion requirement:
  - profile transitions (`core -> enterprise -> regulated`) require successful conformance and evidence gates defined in layer3/layer4 contracts.
