# Glyphser Deployment Runbook Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.DeploymentRunbook`  
**Purpose (1 sentence):** Define deterministic deployment, rollback, and incident-response procedures for dev/staging/prod environments.  
**Spec Version:** `Glyphser.Implementation.DeploymentRunbook` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Operational deployment governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.DeploymentRunbook`
- **Purpose (1 sentence):** Deterministic deployment operations.
- **Spec Version:** `Glyphser.Implementation.DeploymentRunbook` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Release operations and reliability.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize failed rollouts and recovery time.
### 0.B Reproducibility Contract
- Replayable given `(release_manifest_hash, environment_profile, deployment_policy_bundle_hash)`.
### 0.C Numeric Policy
- SLO/SLA thresholds evaluated in binary64.
### 0.D Ordering and Tie-Break Policy
- Deployment stages proceed in strict order: dev -> staging -> prod.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel instance rollout allowed with deterministic canary and gate aggregation.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for gate verdicts and rollback decisions.
### 0.G Operator Manifest
- `Glyphser.Deploy.PreflightChecks`
- `Glyphser.Deploy.ExecuteRollout`
- `Glyphser.Deploy.EvaluateHealthGates`
- `Glyphser.Deploy.ExecuteRollback`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Deployment operators fully-qualified and environment-scoped.
### 0.I Outputs and Metric Schema
- Outputs: `(deployment_report, rollback_report?)`.
- Metrics: `rollout_success_rate`, `mean_recovery_time`, `incident_count`.
- `rollout_success_rate` definition (normative): `(successful_canary_stages / total_canary_stages_attempted) * 100`.
- Completion status: `success | failed | rolled_back`.
### 0.J Spec Lifecycle Governance
- Gate-policy semantic changes require version bump.
### 0.K Failure and Error Semantics
- Abort or rollback on failed critical gates.
### 0.L Input/Data Provenance
- Release artifacts and manifests are hash-addressed and signed.

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
- environment state snapshots and deployment history.
### I.B Inputs and Hyperparameters
- release bundle, target environment, rollout strategy, health thresholds.
### I.C Constraints and Feasible Set
- Valid deployment requires passing preflight + health gates.
### I.D Transient Variables
- canary status, gate diagnostics, rollback cursor.
### I.E Invariants and Assertions
- production promotion only after staging pass.

### II.F Deterministic Rollout Playbook (Concrete)
- Preflight checks: signature verification, dependency lock verification, config-schema validation, checkpoint compatibility check.
- Canary policy: fixed cohort order `[1%, 5%, 25%, 50%, 100%]`, each stage advances on deterministic sample-count windows (not wall-clock dwell).
- Gate thresholds:
  - error_rate <= 0.5%
  - p95_latency_delta <= 10%
  - replay_determinism_failures == 0
  - boundary rule (normative): floating-point threshold checks use `value <= threshold + EPS_EQ` with `EPS_EQ=1e-10`.
- Gate metric definitions (normative):
  - `error_rate` = `failed_requests / total_requests` over the fixed canary evaluation window declared in rollout policy.
  - `p95_latency_delta` = `(p95_latency_canary - p95_latency_baseline) / p95_latency_baseline * 100`, with baseline from the last approved production release bound by `baseline_release_hash`.
  - `replay_determinism_failures` = count of E0 replay-check failures over the same fixed window.
    - failure criterion is a divergence reported by `Glyphser.Replay.CompareTrace` under the applicable comparison profile from `docs/layer2-specs/Replay-Determinism.md`.
  - rollout input MUST include explicit `baseline_release_hash`; baseline selection is not inferred implicitly.
  - All gate metrics are computed from a frozen, canonicalized telemetry snapshot committed as `metrics_snapshot_hash`.
  - `metrics_snapshot_hash = SHA-256(CBOR_CANONICAL(metrics_snapshot_map))`.
- Gate verdict determinism: verdict is computed from a frozen metrics snapshot (`metrics_snapshot_hash`) captured at each canary stage; real-time telemetry ordering is not used directly for final verdict computation.
- Rollback triggers: any threshold breach at any stage, signature mismatch, or missing trace artifacts.
- Promotion gate:
  - production promotion requires valid `ExecutionCertificate` and `EvidenceValidate` pass.
  - Signed-field hash equality checks are mandatory before promotion:
    - `ExecutionCertificate.signed_payload.manifest_hash == release_manifest_hash`
    - `ExecutionCertificate.signed_payload.trace_final_hash == approved_trace_final_hash`
    - `ExecutionCertificate.signed_payload.checkpoint_hash == approved_checkpoint_hash`
    - `ExecutionCertificate.signed_payload.policy_bundle_hash == deployment_policy_bundle_hash`
    - `ExecutionCertificate.signed_payload.lockfile_hash == lockfile_hash`
    - `ExecutionCertificate.signed_payload.dependencies_lock_hash == SHA-256(CBOR_CANONICAL(["deps_lock", [lockfile_hash, toolchain_hash, runtime_env_hash]]))`
    - `ExecutionCertificate.signed_payload.determinism_profile_hash == runtime_determinism_profile_hash`
    - `ExecutionCertificate.signed_payload.operator_contracts_root_hash == operator_contracts_root_hash`
    - `ExecutionCertificate.signed_payload.lineage_root_hash == expected_lineage_root_hash`
- Required logged artifacts: `release_hash`, `sbom_hash`, `gate_report_hash`, `rollback_report_hash` (if rollback executed).
- Artifact commitment formulas:
  - `release_hash = SHA-256(CBOR_CANONICAL(["release", [image_digest, code_commit_hash, lockfile_hash, toolchain_hash]]))`.
  - `image_digest` is the immutable OCI manifest digest (`sha256:<hex>`) resolved from registry manifest bytes.
  - `sbom_hash = SHA-256(sbom_bytes)` where `sbom_bytes` is canonical SPDX JSON (UTF-8, lexicographically sorted object keys, no insignificant whitespace).
- Secrets and keys:
  - secret injection only through managed secret stores,
  - key rotation procedure and rotation audit record required before promotion.
- Transport and isolation requirements:
  - control-plane mTLS required,
  - trust-root pinning policy required,
  - minimum cipher-suite baseline required,
  - namespace/network-policy/storage-path segregation required between tenants/environments.
- Migration/DR:
  - migration playbook must include schema/version compatibility checks and rollback points,
  - disaster recovery artifacts required: last-good checkpoint manifest hash, restore procedure hash, incident timeline log.

### II.G Atomic Run Commit Protocol (Normative)
- Finalization of a run is a deterministic commit-pointer protocol:
  1. write immutable content-addressed trace/checkpoint/lineage/certificate objects,
  2. compute and validate bound hashes,
  3. emit terminal WAL finalize record,
  4. publish single COMMITTED pointer object with `{trace_final_hash, checkpoint_hash, lineage_root_hash, certificate_hash, wal_terminal_hash}` via conditional create-if-absent.
- Crash recovery validates COMMITTED pointer if present; if absent, run remains uncommitted and recovery proceeds from WAL.

### II.H CAS Retention and Garbage Collection (Normative)
- Objects are content-addressed and immutable.
- Retention classes: `golden`, `certified_release`, `experimental`, `ephemeral`.
- Reachability roots include valid execution certificates and pinned model releases.
- GC policy:
  - mark reachable objects from active roots,
  - enforce minimum retention windows by class,
  - sweep only unreachable expired objects.
- GC must never delete objects reachable from active certified artifacts; every deletion emits an auditable hash-chained GC log.

### II.I Key Rotation and Revocation (Normative)
- Signing and redaction keys must declare `key_id`, validity window, and rotation cadence.
- Revocation evidence bundle must be hash-pinned and checked during certificate verification.
- Deployment promotion must fail if signer/redaction keys are revoked or outside validity window at verification time.

---
## 3) Initialization
1. Load release manifest and signatures.
2. Validate environment readiness.
3. Initialize rollout state.

---
## 4) Operator Manifest
- `Glyphser.Deploy.PreflightChecks`
- `Glyphser.Deploy.ExecuteRollout`
- `Glyphser.Deploy.EvaluateHealthGates`
- `Glyphser.Deploy.ExecuteRollback`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `Glyphser.Deploy.PreflightChecks`  
**Category:** IO  
**Signature:** `(release, env -> preflight_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** validates artifact integrity, configuration, and capacity prerequisites.

**Operator:** `Glyphser.Deploy.ExecuteRollout`  
**Category:** IO  
**Signature:** `(release, env, strategy -> rollout_state)`  
**Purity class:** IO  
**Determinism:** deterministic orchestration  
**Definition:** executes staged rollout with deterministic canary sequence.

**Operator:** `Glyphser.Deploy.EvaluateHealthGates`  
**Category:** IO  
**Signature:** `(rollout_state, thresholds -> gate_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** evaluates health and policy gates.

**Operator:** `Glyphser.Deploy.ExecuteRollback`  
**Category:** IO  
**Signature:** `(env, previous_release -> rollback_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** restores previous stable release and validates post-rollback health.

---
## 6) Procedure
```text
1. PreflightChecks
2. ExecuteRollout
3. EvaluateHealthGates
4. If gate failure -> ExecuteRollback
5. Emit deployment report
```

---
## 7) Trace & Metrics
### Logging rule
Every rollout stage emits deterministic operational records.
### Trace schema
- `run_header`: release_hash, env
- `iter`: stage, action, gate_result
- `run_end`: final_status
### Metric schema
- `rollout_success_rate`, `mean_recovery_time`, `incident_count`
### Comparability guarantee
Comparable iff release/gate policies and environment profiles are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes deterministic stage ordering and explicit rollback semantics.
#### VII.B Operator test vectors (mandatory)
Includes preflight, rollout, gate-fail, rollback fixtures.
#### VII.C Golden traces (mandatory)
Golden rollout and rollback traces for baseline releases.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for gate verdict and rollout/rollback decisions.
#### VIII.B Allowed refactor categories
- deployment automation refactor preserving stage/gate semantics.
#### VIII.C Equivalence test procedure (mandatory)
Exact compare of stage transitions and final status.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- rollout cursor, canary set, gate states.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed rollout yields identical stage sequence and decisions.

---
## 11) Packaging and Usage-Metering Addendum (Normative)
- Turnkey deployment artifacts MUST be published per release:
  - versioned Helm chart,
  - versioned Terraform module,
  - hardened default runtime configuration set.
- Upgrade/rollback playbooks MUST be version-locked and evidence-bound.
- Canonical usage record schema (for chargeback/internal accounting):
  - `{tenant_id, run_id, window_start_utc, window_end_utc, cpu_time_ms, gpu_time_ms, io_bytes, storage_bytes_peak, quota_policy_hash, usage_record_hash}`.
- Usage aggregation policy:
  - fixed deterministic windows, no overlapping attribution, stable ordering by `(tenant_id, run_id, window_start_utc)`.
- Enforcement loop rule:
  - quota checks and usage records must be emitted from the same deterministic resource ledger snapshot.
