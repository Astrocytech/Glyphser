# Glyphser Model Registry Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Registry.ModelRegistry`  
**Purpose (1 sentence):** Define deterministic model/version registry and approval gates bound to execution evidence.  
**Spec Version:** `Glyphser.Registry.ModelRegistry` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Model governance and promotion workflows.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Registry.ModelRegistry`
- **Purpose (1 sentence):** Evidence-gated model lifecycle governance.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize ungoverned model promotions.
### 0.B Reproducibility Contract
- Replayable given `(model_id, model_version_id, execution_certificate_hash)`.
### 0.C Numeric Policy
- Version counters exact.
### 0.D Ordering and Tie-Break Policy
- Stage transitions follow deterministic policy graph.
### 0.E Parallel, Concurrency, and Reduction Policy
- Concurrent approvals reduced by deterministic policy precedence.
### 0.F Environment and Dependency Policy
- Registry write requires valid `ExecutionCertificate`.
### 0.G Operator Manifest
- `Glyphser.Registry.ModelCreate`
- `Glyphser.Registry.VersionCreate`
- `Glyphser.Registry.StageTransition`
- `Glyphser.Registry.PolicyGateEvaluate`
- `Glyphser.Registry.ApprovalRecord`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Registry.*` namespace.
### 0.I Outputs and Metric Schema
- Outputs: `(registry_event, gate_report)`
- Metrics: `versions_created`, `stage_transitions`, `gate_failures`
### 0.J Spec Lifecycle Governance
- Governance semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on missing/invalid evidence bundle.
### 0.L Input/Data Provenance
- Every version must bind evidence refs: replay token, trace root, checkpoint hash.

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
- model/version registry, approvals, policy gates.
### I.B Inputs and Hyperparameters
- `Model`, `ModelVersion`, `Stage`, `Approval`, `PolicyGate`, `SBOMRef`, `EvidenceBundleRef`.
### I.C Constraints and Feasible Set
- Stage transition invalid without policy gate pass.
### I.D Transient Variables
- gate diagnostics and approval context.
### I.E Invariants and Assertions
- immutable model version payload; append-only approvals.

### II.F CAS Retention and Reachability (Normative)
- Registry objects must reference immutable content-addressed artifacts.
- Reachability roots include:
  - active model versions in non-terminal retention classes,
  - execution certificates bound to promoted versions.
- GC safety invariant: objects reachable from active roots cannot be deleted; tombstoning is append-only and auditable.

### II.G Registry State Machine (Normative)
- States:
  - model version lifecycle: `CREATED -> STAGED -> APPROVED -> DEPLOYED | REJECTED | ARCHIVED`.
- Legal transitions:
  - `CREATED->STAGED`, `STAGED->APPROVED`, `APPROVED->DEPLOYED`,
  - `STAGED->REJECTED`, `APPROVED->ARCHIVED`, `DEPLOYED->ARCHIVED`.
- Transition invariants:
  - each transition requires valid `evidence_bundle_ref`,
  - transition writes are append-only and keyed by monotone `transition_seq`,
  - retries use deterministic `idempotency_key` and must not duplicate state changes.
  - `idempotency_key = SHA-256(CBOR_CANONICAL([tenant_id, [model_id, model_version_id, transition_seq, from_stage, to_stage]]))`.

### II.H Canonical Registry Record Schemas (Normative)
- `ModelRecord` (CBOR map):
  - `tenant_id:string`, `model_id:string`, `name:string`, `created_by:string`, `created_at:string`, `model_metadata_hash:bytes32`.
- `ModelVersionRecord` (CBOR map):
  - `tenant_id:string`, `model_id:string`, `model_version_id:string`, `checkpoint_hash:bytes32`, `execution_certificate_hash:bytes32`, `manifest_hash:bytes32`, `lineage_root_hash:bytes32`, `artifact_index_hash:bytes32`, `created_at:string`.
- `StageTransitionRecord` (CBOR map):
  - `tenant_id:string`, `model_id:string`, `model_version_id:string`, `transition_seq:uint64`, `from_stage:string`, `to_stage:string`, `policy_gate_hash:bytes32`, `authz_decision_hash:bytes32`, `decision_time:string`, `idempotency_key:bytes32`, `decision_reason_code:string`.
- Record hash rule:
  - `record_hash = SHA-256(CBOR_CANONICAL(record_map))`.

---
## 3) Initialization
1. Load registry schema.
2. Validate RBAC role bindings.
3. Load policy-gate definitions.

---
## 4) Operator Manifest
- `Glyphser.Registry.ModelCreate`
- `Glyphser.Registry.VersionCreate`
- `Glyphser.Registry.StageTransition`
- `Glyphser.Registry.PolicyGateEvaluate`
- `Glyphser.Registry.ApprovalRecord`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
External operator reference: `Glyphser.Error.Emit` in `docs/layer1-foundation/Error-Codes.md`.

**Operator:** `Glyphser.Registry.ModelCreate`  
**Category:** Governance  
**Signature:** `(tenant_id, model_spec -> model_id)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** creates immutable model namespace anchor and canonical metadata record.

**Operator:** `Glyphser.Registry.VersionCreate`  
**Category:** Governance  
**Signature:** `(model_id, artifact_ref, evidence_bundle_ref -> model_version_id)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** creates immutable model version only if evidence bundle is valid.
`evidence_bundle_ref` is a `bytes32` hash of the canonical evidence bundle used for version admission checks (certificate/evaluation/provenance evidence), encoded via canonical CBOR before hashing.

**Operator:** `Glyphser.Registry.PolicyGateEvaluate`  
**Category:** Governance  
**Signature:** `(model_version_id, policy_set -> gate_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** evaluates policy gates including certificate/evidence coherence.

**Operator:** `Glyphser.Registry.ApprovalRecord`  
**Category:** Governance  
**Signature:** `(model_version_id, approver_principal, decision, decision_reason_code, policy_gate_hash -> approval_record_id)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** appends immutable approval decision record with deterministic reason code, explicit `policy_gate_hash`, and authz bindings.

**Operator:** `Glyphser.Registry.StageTransition`  
**Category:** Governance  
**Signature:** `(model_version_id, from_stage, to_stage, policy_gate_hash, authz_decision_hash, approval_record_id -> transition_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** performs validated stage transition only after gate pass and verification that `approval_record_id` exists and matches `(model_version_id, to_stage, policy_gate_hash)`.

---
## 6) Procedure
```text
1. ModelCreate
2. VersionCreate
3. PolicyGateEvaluate
4. ApprovalRecord
5. StageTransition
```

---
## 7) Trace & Metrics
### Logging rule
- Every registry mutation emits deterministic governance events.
### Trace schema
- `run_header`: tenant_id, registry_version
- `iter`: model_version_id, action, status
- `run_end`: final_stage
### Metric schema
- `stage_transitions`, `gate_failures`
### Comparability guarantee
- Comparable iff policy set + evidence validation rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- no stage transition without valid evidence + gate pass.
#### VII.B Operator test vectors (mandatory)
- valid/invalid certificate; approval role violations; gate failures.
#### VII.C Golden traces (mandatory)
- golden model promotion traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for governance decisions and stage transitions.
#### VIII.B Allowed refactor categories
- registry storage changes preserving policy outcomes.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of gate reports + transition logs.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- registry index and policy gate state.
### Serialization
- deterministic CBOR.
### Restore semantics
- restored registry yields identical gate decisions for same inputs.

---
## 11) Export Interface Stability and Marketplace Policy (Normative)
- Exported model artifacts (`model.onnx`, `model_card.json`) are treated as versioned compatibility surfaces.
- Model card schema MUST declare explicit version and compatibility window.
- Third-party publishability policy:
  - operator/module listings in marketplace contexts require:
    - conformance evidence bundle,
    - security/compliance profile declaration,
    - registry-root/hash provenance,
    - deprecation/support window declaration.
- Governance reference:
  - `docs/layer4-implementation/Community-Governance-Model.md`.
