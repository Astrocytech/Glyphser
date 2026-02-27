# Glyphser Repo Layout and Interfaces Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.RepoLayoutInterfaces`  
**Purpose (1 sentence):** Define canonical repository structure, module boundaries, and ownership aligned to operator interface contracts.  
**Spec Version:** `Glyphser.Implementation.RepoLayoutInterfaces` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Implementation architecture and module governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.RepoLayoutInterfaces`
- **Purpose (1 sentence):** Canonical codebase layout and boundary contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize code ownership ambiguity and cross-module contract drift.
### 0.B Reproducibility Contract
- layout and interface manifests are hash-addressed and versioned.
### 0.C Numeric Policy
- N/A except hash and version identifiers.
### 0.D Ordering and Tie-Break Policy
- module resolution order is deterministic lexical path order.
### 0.E Parallel, Concurrency, and Reduction Policy
- build graph resolution deterministic by declared dependencies.
### 0.F Environment and Dependency Policy
- dependency boundaries enforced by static import rules.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Implementation.ValidateRepoLayout`
- `Glyphser.Implementation.ValidateModuleBoundaries`
- `Glyphser.Implementation.ValidateOwnershipMap`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- namespace roots: `src/`, `tests/`, `vectors/`, `schemas/`, `ops/`.
### 0.I Outputs and Metric Schema
- outputs: `(layout_report, boundary_report, ownership_report)`.
### 0.J Spec Lifecycle Governance
- boundary/ownership semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- boundary violations emit deterministic errors.
### 0.L Input/Data Provenance
- repo state bound to commit hash and manifest hash.

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
- module registry and ownership map.
### I.B Inputs and Hyperparameters
- repo tree, module manifest, ownership manifest.
### I.C Constraints and Feasible Set
- every mapped operator must have exactly one module target.
### I.D Transient Variables
- validation diagnostics.
### I.E Invariants and Assertions
- ownership coverage complete for mapped operators.

### II.F Canonical Layout (Normative)
- `src/data`, `src/model`, `src/dp`, `src/tmmu`, `src/replay`, `src/trace`, `src/checkpoint`, `src/backend`, `src/security`, `src/registry`, `src/tracking`, `src/monitor`, `src/cert`.
- `tests/unit`, `tests/integration`, `tests/replay`, `tests/perf`.
- `vectors/<operator_id>/`.
- `schemas/` for config/trace/checkpoint/api schemas.
- `tools/spec_lint.py` mandatory linter entrypoint for cross-file contract consistency.
- `contracts/operator_registry.cbor` canonical machine-readable operator registry artifact.
- Additional authoritative contract artifacts:
  - `contracts/digest_catalog.cbor`
  - `contracts/determinism_profiles.cbor`
  - `wal/run_commit/<tenant_id>/<run_id>/records/<wal_seq>.cbor`
  - `runs/<tenant_id>/<run_id>/COMMITTED` (conditional commit pointer object)

### II.G Ownership Map (Normative)
- `data team`: `src/data/*`
- `model team`: `src/model/*`
- `privacy team`: `src/dp/*`
- `runtime team`: `src/tmmu/*`, `src/checkpoint/*`
- `platform team`: `src/tracking/*`, `src/monitor/*`, `src/config/*`
- `security team`: `src/security/*`, `src/cert/*`
- `governance team`: `src/registry/*`

### II.H Operator Registry Artifact (Normative)
- `contracts/operator_registry.cbor` is the single source of truth for operator interface metadata.
- construction and validation contract: `docs/layer4-implementation/Operator-Registry-CBOR-Contract.md`.
- Required fields per operator record:
  - `operator_id`, `version`, `surface`,
  - `request_schema_digest`, `response_schema_digest`, `signature_digest`,
  - `side_effects`, `allowed_error_codes`, `purity_class`, `required_capabilities`.
- `docs/layer1-foundation/API-Interfaces.md` and `docs/layer4-implementation/Code-Generation-Mapping.md` are rendered/derived views and must not diverge from the artifact.
- Any divergence is a deterministic `CONTRACT_VIOLATION` at lint time.

---
## 3) Initialization
1. Load repo layout manifest.
2. Load ownership manifest.
3. Load operator mapping manifest.

---
## 4) Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Implementation.ValidateRepoLayout`
- `Glyphser.Implementation.ValidateModuleBoundaries`
- `Glyphser.Implementation.ValidateOwnershipMap`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Implementation.ValidateRepoLayout`  
**Category:** Implementation  
**Signature:** `(repo_tree, layout_contract -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks required directories/files and canonical placement rules.

**Operator:** `Glyphser.Implementation.ValidateModuleBoundaries`  
**Category:** Implementation  
**Signature:** `(import_graph, boundary_rules -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** enforces allowed dependencies and forbids boundary leaks.

---
## 6) Procedure
```text
1. ValidateRepoLayout
2. ValidateModuleBoundaries
3. ValidateOwnershipMap
4. Emit reports and fail on violations
```

---
## 7) Trace & Metrics
### Logging rule
- repository validation emits deterministic structural diagnostics.
### Trace schema
- `run_header`: commit_hash, mapping_hash
- `iter`: module_id, check_id, status
- `run_end`: violation_count
### Metric schema
- `missing_paths`, `boundary_violations`, `ownership_gaps`
### Comparability guarantee
- comparable iff repo snapshot and contracts are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- every mapped API operator has exactly one repo module target.
#### VII.B Operator test vectors (mandatory)
- valid/invalid layout trees and boundary graphs.
#### VII.C Golden traces (mandatory)
- golden layout validation traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for reports and violation counts.
#### VIII.B Allowed refactor categories
- tooling implementation changes preserving validation semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of reports for golden repo snapshots.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- validator cursor and partial diagnostics.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed validation yields identical final report.
