# Glyphser Compatibility Test Matrix
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.CompatibilityMatrix`  
**Purpose (1 sentence):** Define deterministic compatibility testing across schema versions, migrations, and runtime profiles.  
**Spec Version:** `Glyphser.Test.CompatibilityMatrix` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Backward/forward compatibility validation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.CompatibilityMatrix`
- **Purpose (1 sentence):** Deterministic compatibility matrix contract.
### 0.A Objective Semantics
- minimize unsupported version pairings and migration regressions.
### 0.B Reproducibility Contract
- matrix verdict reproducible from `(matrix_version, migration_rules_hash, vectors_catalog_hash)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- counters and version indices are exact.
### 0.D Ordering and Tie-Break Policy
- pairings sorted by `(from_version, to_version, artifact_type)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- pairwise tests parallelized; verdict aggregation deterministic.
### 0.F Environment and Dependency Policy
- compatibility runner pinned to deterministic toolchain.
### 0.G Operator Manifest
- `Glyphser.Test.RunCompatibilityCase`
- `Glyphser.Test.VerifyMigrationPath`
- `Glyphser.Test.AggregateCompatibilityVerdict`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Test.*` and migration namespaces.
### 0.I Outputs and Metric Schema
- outputs: `(compatibility_report, compatibility_verdict, unsupported_pairs)`.
### 0.J Spec Lifecycle Governance
- matrix policy changes are MAJOR.
### 0.K Failure and Error Semantics
- missing migration path is deterministic failure.
### 0.L Input/Data Provenance
- all test artifacts are content-addressed.
### 0.Z EQC Mandatory Declarations Addendum
- seed space: `uint64` (only if stochastic fixture generation is enabled by matrix policy).
- PRNG family: `Philox4x32-10` when stochastic generation is enabled; otherwise N/A.
- replay guarantee: same `(matrix_version, migration_rules_hash, vectors_catalog_hash)` yields identical `(compatibility_report, compatibility_verdict, unsupported_pairs)`.
- floating-point format: IEEE-754 binary64; rounding mode `roundTiesToEven`.
- NaN/Inf policy: prohibited in verdict-bearing metrics; encountering either is deterministic failure.
- default tolerances: `abs_tol=EPS_EQ`, `rel_tol=0` unless explicitly overridden by case profile.
- determinism target: E0 for final verdict and unsupported pair identities.

---
## 2) System Model
### I.A Persistent State
- compatibility matrix definition and migration registry.
### I.B Inputs and Hyperparameters
- schema families, version ranges, profile id, and the vectors catalog commitment (`vectors_catalog_hash`) used for fixtures.
### I.C Constraints and Feasible Set
- only declared migration paths are allowed.
### I.D Transient Variables
- per-pair test outcomes.
### I.E Invariants and Assertions
- identical pair input yields identical verdict.

---
## 3) Initialization
1. Load matrix definition and migration rules.
2. Resolve version pair set.
3. Initialize result accumulator.

---
## 4) Operator Manifest
- `Glyphser.Test.RunCompatibilityCase`
- `Glyphser.Test.VerifyMigrationPath`
- `Glyphser.Test.AggregateCompatibilityVerdict`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Test.RunCompatibilityCase`  
**Signature:** `(artifact_type, from_version, to_version, fixture -> case_result)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Executes one compatibility test with deterministic pass/fail criteria.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `MIGRATION_PATH_MISSING`, `VECTOR_LOAD_FAILURE`.

**Operator:** `Glyphser.Test.VerifyMigrationPath`
**Signature:** `(artifact_type, from_version, to_version, migration_rules_hash -> migration_report)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Verifies that a declared deterministic migration path exists and is admissible for the version pair.
**allowed_error_codes:** `MIGRATION_PATH_MISSING`, `CONTRACT_VIOLATION`.

**Operator:** `Glyphser.Test.AggregateCompatibilityVerdict`
**Signature:** `(case_results, migration_reports -> compatibility_report, compatibility_verdict, unsupported_pairs)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Deterministically aggregates per-pair outcomes into final report, verdict, and unsupported pair list.
**allowed_error_codes:** `CONTRACT_VIOLATION`.

---
## 6) Procedure
```text
1. Enumerate compatibility pairs
2. Validate migration path per pair
3. Execute compatibility case
4. Aggregate matrix verdict and emit `(compatibility_report, compatibility_verdict, unsupported_pairs)`
```

---
## 7) Trace & Metrics
- Metrics: `pairs_total`, `pairs_passed`, `pairs_failed`, `unsupported_count`.
- Trace includes artifact type, from/to versions, case verdict.

---
## 8) Validation
- golden compatibility matrix fixtures.
- migration path edge-case tests.

---
## 9) Refactor & Equivalence
- E0 for matrix verdict and unsupported pair list.

---
## 10) Checkpoint/Restore
- checkpoint stores case cursor and partial matrix hash.
- restore resumes matrix execution deterministically.

---
## 11) Published Compatibility Guarantees (Normative)
- Matrix output MUST include a customer-facing compatibility table by profile:
  - supported version ranges,
  - required migration operators,
  - unsupported pair rationale codes.
- Compatibility table hash:
  - `compatibility_table_hash = SHA-256(CBOR_CANONICAL(compatibility_table))`.
- Release consumers may rely on published compatibility table as normative contract for upgrade planning.
