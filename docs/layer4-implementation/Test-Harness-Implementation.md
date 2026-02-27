# Glyphser Test Harness Implementation Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.HarnessImplementation`  
**Purpose (1 sentence):** Define deterministic harness architecture for loading vectors, executing suites, and evaluating outcomes.  
**Spec Version:** `Glyphser.Test.HarnessImplementation` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Test harness implementation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.HarnessImplementation`
- **Purpose (1 sentence):** Deterministic harness execution model.
### 0.A Objective Semantics
- minimize flaky or ambiguous test outcomes.
### 0.B Reproducibility Contract
- harness verdict reproducible from `(vectors_catalog_hash, harness_config_hash)`.
### 0.C Numeric Policy
- binary64 for metric comparisons unless exact hashes required.
### 0.D Ordering and Tie-Break Policy
- vector execution order by `(suite_id, vector_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- parallel vector execution allowed with deterministic result merge.
### 0.F Environment and Dependency Policy
- harness env pinned; deterministic profile required.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Test.LoadVectorSet`
- `Glyphser.Test.ExecuteVector`
- `Glyphser.Test.CompareExpected`
- `Glyphser.Test.AggregateHarnessReport`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Test.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(suite_results, harness_report, harness_verdict)`.
### 0.J Spec Lifecycle Governance
- comparator semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- malformed vectors or comparator mismatch fail deterministically.
### 0.L Input/Data Provenance
- vectors loaded by content hash.

---
## 2) System Model
### I.A Persistent State
- harness config and comparator registry.
### I.B Inputs and Hyperparameters
- suite ids, vector catalog, comparison profile.
### I.C Constraints and Feasible Set
- every vector must declare expected output or expected error.
### I.D Transient Variables
- per-vector runtime outputs.
### I.E Invariants and Assertions
- every vector produces exactly one terminal result.

---
## 3) Initialization
1. Load vectors catalog.
2. Validate harness configuration.
3. Initialize comparator state.

---
## 4) Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Test.LoadVectorSet`
- `Glyphser.Test.ExecuteVector`
- `Glyphser.Test.CompareExpected`
- `Glyphser.Test.AggregateHarnessReport`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Test.CompareExpected`  
**Signature:** `(observed, expected, compare_profile -> verdict)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Compares outputs with exact or tolerance profile rules and emits canonical verdict.

---
## 6) Procedure
```text
1. Load vectors for selected suites
2. Execute each vector deterministically
3. Compare observed vs expected
4. Aggregate suite and harness verdict
```

---
## 7) Trace & Metrics
- Metrics: `vectors_total`, `vectors_passed`, `vectors_failed`, `suite_failures`.
- Trace includes vector ids, operator ids, compare profile hash.

---
## 8) Validation
- harness self-tests with meta-vectors.
- deterministic ordering and report hash tests.

---
## 9) Refactor & Equivalence
- E0 for vector verdicts and harness report hash.

---
## 10) Checkpoint/Restore
- checkpoint stores vector cursor and accumulated results hash.
- restore resumes without changing final verdict.
