# Glyphser Integration Test Matrix Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.IntegrationMatrix`  
**Purpose (1 sentence):** Define deterministic cross-module integration suites and pass/fail semantics for end-to-end Glyphser correctness.  
**Spec Version:** `Glyphser.Test.IntegrationMatrix` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** System integration verification.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.IntegrationMatrix`
- **Purpose (1 sentence):** Deterministic integration coverage contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: maximize deterministic end-to-end contract coverage.
### 0.B Reproducibility Contract
- Replayable given `(integration_matrix_hash, test_manifest_hash, seeds)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- Result comparisons use E0/E1 policy declared per suite.
### 0.D Ordering and Tie-Break Policy
- Suites execute in fixed matrix order.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel suite runs allowed; verdict merge deterministic.
### 0.F Environment and Dependency Policy
- Same environment constraints as release CI.
### 0.G Operator Manifest
- `Glyphser.Test.RunIntegrationCase`
- `Glyphser.Test.CompareIntegrationOutputs`
- `Glyphser.Test.EvaluateIntegrationMatrix`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `tests/integration/<suite>/<case>`
### 0.I Outputs and Metric Schema
- Outputs: `(integration_report, matrix_verdict)`
- Metrics: `cases_total`, `cases_passed`, `cases_failed`
### 0.J Spec Lifecycle Governance
- Required suite changes are MAJOR.
### 0.K Failure and Error Semantics
- Any required case failure fails matrix.
### 0.L Input/Data Provenance
- Each case must bind fixture and expected digest refs.
### 0.Z EQC Mandatory Declarations Addendum
- seed space: `uint64` (per-case seeds are part of fixtures).
- PRNG family: `Philox4x32-10` for stochastic case fixtures.
- replay guarantee: identical `(integration_matrix_hash, test_manifest_hash, seeds)` and fixture digests yield identical `matrix_verdict`.
- floating-point format: IEEE-754 binary64; rounding mode `roundTiesToEven`.
- NaN/Inf policy: invalid for verdict-bearing comparisons unless explicitly declared by case profile.
- default tolerances: `abs_tol=EPS_EQ`, `rel_tol=0` for E1 when omitted.
- determinism target: E0 for required-case pass/fail and matrix verdict.

---
## 2) System Model
### I.A Persistent State
- Integration matrix definition and golden outputs.
### I.B Inputs and Hyperparameters
- `integration_matrix_hash`, `test_manifest_hash`, case fixtures (including deterministic `seeds`), expected outputs, tolerances, modes.
### I.C Constraints and Feasible Set
- Valid iff all required cases execute and compare successfully.
- `required` means cases marked `mandatory=true` in the matrix definition.
### I.D Transient Variables
- case outputs and diff diagnostics.
### I.E Invariants and Assertions
- Every interface boundary appears in at least one integration case.

---
## 3) Initialization
1. Load matrix and fixtures.
2. Validate case signatures against registry.
3. Initialize deterministic suite order.

---
## 4) Operator Manifest
- `Glyphser.Test.RunIntegrationCase`
- `Glyphser.Test.CompareIntegrationOutputs`
- `Glyphser.Test.EvaluateIntegrationMatrix`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Test.RunIntegrationCase`  
**Signature:** `(case_id, fixture -> case_output)`  
**Purity class:** IO  
**Determinism:** deterministic with fixed seeds.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `CASE_FIXTURE_MISSING`, `EXECUTION_FAILURE`.

**Operator:** `Glyphser.Test.CompareIntegrationOutputs`  
**Signature:** `(case_output, expected_output, comparison_profile -> compare_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.
`comparison_profile` schema: `{equivalence_class: "E0"|"E1", abs_tol?: float64, rel_tol?: float64}` with deterministic defaults `abs_tol=EPS_EQ`, `rel_tol=0` when omitted.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `COMPARE_PROFILE_INVALID`, `OUTPUT_MISMATCH`.

**Operator:** `Glyphser.Test.EvaluateIntegrationMatrix`  
**Signature:** `(case_reports, matrix_policy -> matrix_verdict)`  
**Purity class:** PURE  
**Determinism:** deterministic.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `REQUIRED_CASE_MISSING`.

---
## 6) Procedure
```text
1. RunIntegrationCase for each case
2. CompareIntegrationOutputs
3. EvaluateIntegrationMatrix
4. Emit integration_report
```

---
## 7) Trace & Metrics
### Logging rule
- Integration suites emit deterministic case records.
### Trace schema
- `run_header`: matrix_hash, fixture_set_hash
- `iter`: case_id, status, output_hash
- `run_end`: matrix_verdict
### Metric schema
- `cases_total`, `cases_passed`, `cases_failed`
### Comparability guarantee
- Comparable iff same matrix, fixtures, and profile.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Required cross-module boundaries covered.
#### VII.B Operator test vectors (mandatory)
- Case-run/compare/evaluate vectors.
#### VII.C Golden traces (mandatory)
- Golden integration matrix traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for matrix verdict and required case hashes.
#### VIII.B Allowed refactor categories
- Harness/runtime changes preserving case outputs.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of required case reports.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- `case_cursor`, `completed_case_ids[]`, `partial_case_reports_hash`, `current_matrix_accumulator_hash`.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed integration run must preserve final verdict.
