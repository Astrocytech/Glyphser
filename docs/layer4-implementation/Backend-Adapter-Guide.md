# Glyphser Backend Adapter Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Backend.AdapterContract`  
**Purpose (1 sentence):** Define required backend adapter primitives, determinism guarantees, and certification checks for Glyphser driver integration.  
**Spec Version:** `Glyphser.Backend.AdapterContract` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Driver integration and compliance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Backend.AdapterContract`
- **Purpose (1 sentence):** Deterministic backend adapter requirements.
- **Spec Version:** `Glyphser.Backend.AdapterContract` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Backend certification.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize contract violations and reproducibility drift.
### 0.B Reproducibility Contract
- Replayable given `(backend_binary_hash, driver_runtime_fingerprint_hash, adapter_version, test_manifest_hash)`.
### 0.C Numeric Policy
- Critical operations must satisfy binary64 deterministic requirements.
### 0.D Ordering and Tie-Break Policy
- Primitive dispatch order follows ModelIR execution order.
### 0.E Parallel, Concurrency, and Reduction Policy
- Deterministic collective ordering and reductions required.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for critical paths; `TOLERANCE` where declared.
### 0.G Operator Manifest
- `Glyphser.Backend.ValidatePrimitiveCoverage`
- `Glyphser.Backend.RunReproducibilitySuite`
- `Glyphser.Backend.VerifyDriverHash`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Backend operators fully-qualified and versioned.
### 0.I Outputs and Metric Schema
- Outputs: `(adapter_report, certification_status)`.
- Metrics: `covered_primitives`, `e0_pass_rate`, `e1_pass_rate`.
- Completion status: `success | failed`.
- `adapter_report` must include `primitive_semantics_hash` and `determinism_compliance_report_hash`.
### 0.J Spec Lifecycle Governance
- Primitive contract changes require MAJOR bump.
### 0.K Failure and Error Semantics
- Abort on coverage gap, determinism failure, hash mismatch.
### 0.L Input/Data Provenance
- Driver binary, manifest, and test artifacts must be hash-addressed.

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
- driver certification registry.
### I.B Inputs and Hyperparameters
- driver binaries, primitive tables, test manifests.
### I.C Constraints and Feasible Set
- Valid if coverage + reproducibility criteria pass.
### I.D Transient Variables
- per-test verdicts and mismatch diagnostics.
### I.E Invariants and Assertions
- declared primitives map 1:1 to implemented dispatch handlers.

### II.F Required Primitive Catalog
| primitive | determinism_tier_required | allowed_algorithms | required_flags | required_tests |
|---|---|---|---|---|
| `matmul` | E0 same-build / E1 cross-hw | deterministic GEMM kernel set | fast-math off | exact tiny-graph gradient tests |
| `softmax` | E0 | stable log-sum-exp | deterministic reduction | overflow/underflow golden traces |
| `layernorm` | E0 | fixed-order reductions | deterministic accumulation | epsilon sensitivity vectors |
| `rng_gaussian` | E2 with deterministic offsets | Philox-based | declared stream ownership | replay offset tests |
| `all_reduce_sum` | E0 in class | fixed ring/tree order | stable rank order | multi-rank reproducibility suite |

### II.G GPU Determinism Profile (Required)
- TF32 policy must be explicitly declared (`enabled` or `disabled`) and captured in run metadata.
- cuDNN/cuBLAS algorithm selection must use deterministic allow-list only.
- Atomic reduction kernels are forbidden for E0 paths unless deterministic ordering is proven.
- NCCL/all-reduce ordering must be fixed and rank-stable; environment variables affecting ordering must be pinned and captured.
- Effective profile must be exported as `determinism_profile_hash` and bound into replay token context.

### II.H Backend Signature Lock (Normative)
- Backend-exposed syscall/primitive bindings must publish `signature_digest`:
- `signature_digest` rule is defined normatively in `docs/layer1-foundation/Operator-Registry-Schema.md` (`sig` preimage over resolved digest values); backend adapter manifests must match exactly.
- Cross-file invariant:
  - `API-Interfaces.signature_digest(op) == Code-Generation-Mapping.signature_digest(op) == Backend-Adapter-Guide.signature_digest(op)` for every backend-exposed operator.
- Minimum backend-exposed digest set:
  - `Glyphser.Model.Forward -> sha256:17d85435fe2e601fe522b614938ea7853b9c36be14c8feb84f4e70e1e253bc74`
  - `Glyphser.Model.ModelIR_Executor -> sha256:ce1ec3e5cead31a92f46e79847332d3db0fdd824f2f3b6608987c77450a6de70`
  - `Glyphser.Backend.LoadDriver -> sha256:708fd111f6fc0a8f85853a4218ff9eba82ffc3da285266b15f6714a450728056`
- Proof-carrying backend requirements:
  - each primitive declares `primitive_semantics_hash`,
  - backend emits `determinism_compliance_report_hash`,
  - execution is forbidden when backend semantics hash set mismatches approved IR operator set hash.

### II.I Backend/Driver Identity Naming (Normative)
- Canonical identities:
  - `backend_binary_hash:bytes32` = hash of adapter binary/package artifact.
  - `driver_runtime_fingerprint_hash:bytes32` = hash of canonical runtime/driver fingerprint map.
- Multi-backend runs:
  - `backend_binary_hashes: map<string,bytes32>` with canonical key ordering.
- Deprecated aliases:
  - `driver_hash` and `backend_hash` are non-authoritative aliases and must not be used for checkpoint/certificate commitments.

### II.J External Certification Program (Normative)
- Certification label format:
  - `Glyphser Certified Backend v<adapter_contract_version>`.
- Mandatory publishable evidence bundle for certification:
  - `adapter_report`,
  - `primitive_semantics_hash`,
  - `determinism_compliance_report_hash`,
  - `backend_binary_hash`,
  - `driver_runtime_fingerprint_hash`,
  - conformance harness report hashes,
  - signed certification statement hash.
- Vendor-facing verification requirement:
  - published evidence must be independently verifiable using `docs/layer4-implementation/Release-Evidence-Assembler.md` and `docs/layer3-tests/Conformance-Harness-Guide.md`.

---
## 3) Initialization
1. Load driver metadata.
2. Verify signatures/hashes.
3. Build primitive coverage map.

---
## 4) Operator Manifest
- `Glyphser.Backend.ValidatePrimitiveCoverage`
- `Glyphser.Backend.RunReproducibilitySuite`
- `Glyphser.Backend.VerifyDriverHash`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `Glyphser.Backend.ValidatePrimitiveCoverage`  
**Category:** IO  
**Signature:** `(required_primitives, adapter_table -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates primitive coverage and signature compatibility.

**Operator:** `Glyphser.Backend.RunReproducibilitySuite`  
**Category:** IO  
**Signature:** `(driver, test_manifest -> adapter_report)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic suite orchestration and deterministic report reduction order  
**Definition:** runs E0/E1 reproducibility checks vs reference backend and returns:
- `adapter_report.repro_report`
- `adapter_report.primitive_semantics_hash`
- `adapter_report.determinism_compliance_report_hash`.

**Operator:** `Glyphser.Backend.VerifyDriverHash`  
**Category:** IO  
**Signature:** `(driver_binary, registry -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** verifies driver hash against trusted registry.

---
## 6) Procedure
```text
1. VerifyDriverHash
2. ValidatePrimitiveCoverage
3. adapter_report <- RunReproducibilitySuite
4. Emit certification_status from deterministic policy reduction over adapter_report
5. return (adapter_report, certification_status)
```

---
## 7) Trace & Metrics
### Logging rule
Certification emits deterministic per-test records.
### Trace schema
- `run_header`: backend_binary_hash, driver_runtime_fingerprint_hash, adapter_version
- `iter`: test_id, result
- `run_end`: certification_status
### Metric schema
- `covered_primitives`, `e0_pass_rate`, `e1_pass_rate`
### Comparability guarantee
Comparable iff test manifests and reference backend version match.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Ensures completeness, deterministic ordering, and declared failure semantics.
#### VII.B Operator test vectors (mandatory)
Coverage/mismatch and hash validation fixtures.
#### VII.C Golden traces (mandatory)
Golden certification reports for approved drivers.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for certification verdict and critical test outputs.
#### VIII.B Allowed refactor categories
- test harness optimization preserving verdicts.
#### VIII.C Equivalence test procedure (mandatory)
Exact certification report comparison.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- certification progress and per-test outputs.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed certification yields identical final verdict.
