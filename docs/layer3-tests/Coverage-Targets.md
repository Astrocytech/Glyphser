# Glyphser Coverage Targets Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.CoverageTargets`  
**Purpose (1 sentence):** Define deterministic test coverage targets and enforcement rules by subsystem and test type.  
**Spec Version:** `Glyphser.Test.CoverageTargets` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Test quality governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.CoverageTargets`
- **Purpose (1 sentence):** Deterministic coverage gate contract.
### 0.A Objective Semantics
- Optimization sense: `MAXIMIZE`
- Objective type: `Vector`
- Primary objective: enforce minimum coverage across required test classes.
### 0.B Reproducibility Contract
- Replayable given `(coverage_policy_hash, test_report_hash, source_manifest_hash)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- Coverage percentages use binary64; gate checks use exact threshold comparisons.
### 0.D Ordering and Tie-Break Policy
- Coverage aggregation order fixed by subsystem id.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel test execution allowed; coverage reduction deterministic.
### 0.F Environment and Dependency Policy
- Coverage tools and configs must be pinned.
### 0.G Operator Manifest
- `Glyphser.Test.ComputeCoverage`
- `Glyphser.Test.ValidateCoverageTargets`
- `Glyphser.Test.EmitCoverageVerdict`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Coverage artifacts under `reports/coverage/`.
### 0.I Outputs and Metric Schema
- Outputs: `(coverage_report, coverage_verdict)`
- Metrics: `line_cov`, `branch_cov`, `integration_cov`, `replay_cov`
  - `integration_cov`: coverage over integration-suite-tagged source/test mappings.
  - `replay_cov`: coverage over replay/restore determinism code paths and assertions.
### 0.J Spec Lifecycle Governance
- Required thresholds changes are MAJOR.
### 0.K Failure and Error Semantics
- Missing required coverage class fails gate.
### 0.L Input/Data Provenance
- Coverage reports must reference exact source and test manifests.
### 0.Z EQC Mandatory Declarations Addendum
- seed space: N/A (coverage aggregation is deterministic and non-stochastic).
- PRNG family: N/A.
- replay guarantee: identical `(coverage_policy_hash, test_report_hash, source_manifest_hash)` yields identical `(coverage_report, coverage_verdict)`.
- floating-point format: IEEE-754 binary64; rounding mode `roundTiesToEven`.
- NaN/Inf policy: invalid in coverage metrics; deterministic failure if encountered.
- default tolerances: `abs_tol=EPS_EQ`, `rel_tol=0` for threshold boundary checks.
- determinism target: E0 for coverage verdict and normalized metric set.

---
## 2) System Model
### I.A Persistent State
- Coverage policy and historical snapshots.
### I.B Inputs and Hyperparameters
- Raw coverage reports, thresholds, subsystem map, `test_report_hash` (or deterministic derivation `SHA-256(CBOR_CANONICAL(raw_reports))`), and `source_manifest_hash`.
### I.C Constraints and Feasible Set
- Pass iff all required thresholds pass.
### I.D Transient Variables
- normalized coverage metrics and diagnostics.
### I.E Invariants and Assertions
- No threshold evaluation on incomplete report sets.

---
## 3) Initialization
1. Load coverage policy.
2. Load and validate coverage inputs.
3. Normalize coverage schema.

---
## 4) Operator Manifest
- `Glyphser.Test.ComputeCoverage`
- `Glyphser.Test.ValidateCoverageTargets`
- `Glyphser.Test.EmitCoverageVerdict`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Test.ComputeCoverage`  
**Signature:** `(raw_reports -> coverage_metrics)`  
**Purity class:** PURE  
**Determinism:** deterministic.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `COVERAGE_REPORT_INVALID`.

**Operator:** `Glyphser.Test.ValidateCoverageTargets`  
**Signature:** `(coverage_metrics, policy -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `COVERAGE_THRESHOLD_INVALID`.

**Operator:** `Glyphser.Test.EmitCoverageVerdict`  
**Signature:** `(validation_report -> coverage_verdict)`  
**Purity class:** IO  
**Determinism:** deterministic.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `COVERAGE_GATE_FAILED`.

---
## 6) Procedure
```text
1. ComputeCoverage
2. ValidateCoverageTargets
3. EmitCoverageVerdict
4. Return coverage_report
```

---
## 7) Trace & Metrics
### Logging rule
- Coverage evaluation emits deterministic metric and gate records.
### Trace schema
- `run_header`: coverage_policy_hash, source_manifest_hash
- `iter`: subsystem_id, metric_name, metric_value
- `run_end`: coverage_verdict
### Metric schema
- `line_cov`, `branch_cov`, `integration_cov`, `replay_cov`
### Comparability guarantee
- Comparable iff same policy and source/test manifests.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Required coverage classes must be present.
#### VII.B Operator test vectors (mandatory)
- Coverage boundary and missing-report fixtures.
#### VII.C Golden traces (mandatory)
- Golden coverage-gate traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for coverage verdict and normalized metrics.
#### VIII.B Allowed refactor categories
- Coverage tooling changes preserving normalized outputs.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare on frozen coverage inputs.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- Coverage aggregation cursor, per-subsystem partial reductions, and `partial_coverage_report_hash`.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed evaluation yields identical verdict and report.
