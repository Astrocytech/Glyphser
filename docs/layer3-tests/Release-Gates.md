# Glyphser Release Gates Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.ReleaseGates`  
**Purpose (1 sentence):** Define deterministic merge/release gating criteria across correctness, replay, security, and performance evidence.  
**Spec Version:** `Glyphser.Implementation.ReleaseGates` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Release readiness governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.ReleaseGates`
- **Purpose (1 sentence):** Deterministic release decision contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: prevent non-compliant builds from release/promotion.
### 0.B Reproducibility Contract
- Replayable given `(release_manifest_hash, gate_policy_hash, evidence_bundle_hash)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- Threshold checks use deterministic binary64/integer rules.
### 0.D Ordering and Tie-Break Policy
- Gate evaluation order is fixed and versioned.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel evidence gathering allowed; verdict reduction deterministic.
### 0.F Environment and Dependency Policy
- Release gate requires valid env/lock/profile bindings.
### 0.G Operator Manifest
- `Glyphser.Release.CollectEvidence`
- `Glyphser.Release.EvaluateGates`
- `Glyphser.Release.EmitVerdict`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Release.*`
### 0.I Outputs and Metric Schema
- Outputs: `(release_verdict, release_gate_report)`
- Metrics: `gates_total`, `gates_passed`, `gates_failed`
### 0.J Spec Lifecycle Governance
- Gate set changes are MAJOR.
### 0.K Failure and Error Semantics
- Any required gate failure is deterministic release block.
### 0.L Input/Data Provenance
- Release decision must cite all evidence hashes.
### 0.Z EQC Mandatory Declarations Addendum
- seed space: N/A (gate evaluation is deterministic and non-stochastic).
- PRNG family: N/A.
- replay guarantee: identical `(release_manifest_hash, gate_policy_hash, evidence_bundle_hash)` yields identical `release_verdict`.
- floating-point format: IEEE-754 binary64 for threshold math; rounding mode `roundTiesToEven`.
- NaN/Inf policy: invalid in gate metrics; deterministic failure.
- default tolerances: `abs_tol=EPS_EQ`, `rel_tol=0` unless gate policy overrides.
- determinism target: E0 for `release_verdict` and failing gate ids.

---
## 2) System Model
### I.A Persistent State
- Release gate policy and historical verdict ledger.
### I.B Inputs and Hyperparameters
- CI report, test report, replay report, cert report, perf report, security report, and derived `evidence_bundle_hash`.
### I.C Constraints and Feasible Set
- Release allowed iff all required gates pass.
### I.D Transient Variables
- gate diagnostics and final verdict object.
### I.E Invariants and Assertions
- No unbound evidence accepted.

---
## 3) Initialization
1. Load gate policy.
2. Resolve evidence refs.
3. Validate evidence integrity.

---
## 4) Operator Manifest
- `Glyphser.Release.CollectEvidence`
- `Glyphser.Release.EvaluateGates`
- `Glyphser.Release.EmitVerdict`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Release.CollectEvidence`  
**Signature:** `(release_candidate_id -> evidence_bundle, evidence_bundle_hash)`  
**Purity class:** IO  
**Determinism:** deterministic.
**Definition:** Collects canonical release evidence and emits deterministic `evidence_bundle_hash`.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `EVIDENCE_MISSING`, `ARTIFACT_MISSING`.

**Operator:** `Glyphser.Release.EvaluateGates`  
**Signature:** `(evidence_bundle, gate_policy -> gate_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `GATE_POLICY_INVALID`.

**Operator:** `Glyphser.Release.EmitVerdict`  
**Signature:** `(gate_report -> release_verdict)`  
**Purity class:** IO  
**Determinism:** deterministic.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `RELEASE_BLOCKED`.

---
## 6) Procedure
```text
1. CollectEvidence
2. EvaluateGates
3. EmitVerdict
4. Return release_verdict
```

---
## 7) Trace & Metrics
### Logging rule
- Release-gate pipeline emits deterministic gate records.
### Trace schema
- `run_header`: release_candidate_id, gate_policy_hash
- `iter`: gate_id, status, evidence_hash
- `run_end`: release_verdict, report_hash
### Metric schema
- `gates_total`, `gates_passed`, `gates_failed`
### Comparability guarantee
- Comparable iff gate policy and evidence bundle are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- All required gates present and evaluated.
#### VII.B Operator test vectors (mandatory)
- Gate pass/fail boundary vectors.
#### VII.C Golden traces (mandatory)
- Golden release-gate traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for release verdict and report hash.
#### VIII.B Allowed refactor categories
- Tooling/aggregation changes preserving gate semantics.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of gate reports on fixed evidence.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- `gate_cursor`, `completed_gate_ids[]`, `partial_gate_report_hash`, and `evidence_bundle_hash`.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed gate evaluation must produce identical verdict.

---
## 11) External Verification Gate Extensions (Normative)
- For `enterprise` and `regulated` release profiles, release gates MUST include:
  - backend certification evidence bundle verification,
  - artifact-store certification evidence bundle verification,
  - observability mapping hash verification,
  - platform-tier performance baseline verification.
- For `regulated` profile, release gates MUST additionally include:
  - mandatory chaos/recovery proof-pack verification.
- Missing any required external-verification artifact is deterministic release block.

---
## 12) Conformance Coverage Gate (Normative)
- Conformance coverage is a hard release requirement (not advisory).
- Minimum required coverage by profile:
  - `core`: `coverage_pct >= 95.0` and zero `required_operator` blockers.
  - `enterprise`: `coverage_pct >= 98.0` and zero blockers.
  - `regulated`: `coverage_pct == 100.0` and zero blockers.
- Coverage source of truth:
  - `docs/layer4-implementation/Operator-Conformance-Matrix.md` output bundle.
- Any unresolved blocker in required operator sets MUST produce deterministic `RELEASE_BLOCKED`.

- External-auditor references:
  - `docs/layer4-implementation/Evidence-Catalog.md`
  - `docs/layer4-implementation/Benchmark-Evidence-Spec.md`
  - `docs/layer4-implementation/Security-Case-Template.md`

## 13) Pinned Gate Fixture Inputs (Normative)
- Release-gate dry-run pin set:
  - `contracts/catalog-manifest.json`
  - `fixtures/hello-core/fixture-manifest.json`
  - `goldens/hello-core/golden-manifest.json`
  - `vectors/hello-core/vectors-manifest.json`
- Deterministic verification command:
  - `python tools/verify_doc_artifacts.py`
