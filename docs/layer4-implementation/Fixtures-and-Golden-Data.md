# Glyphser Fixtures and Golden Data Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.FixturesGoldenData`  
**Purpose (1 sentence):** Define deterministic fixture and golden-data lifecycle, storage, and update rules for tests and replay validation.  
**Spec Version:** `Glyphser.Test.FixturesGoldenData` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Test fixture governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.FixturesGoldenData`
- **Purpose (1 sentence):** Deterministic fixture/golden governance.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: prevent fixture/golden drift.
### 0.B Reproducibility Contract
- Replayable given `(fixture_set_hash, golden_set_hash, vector_catalog_hash)`.
### 0.C Numeric Policy
- Golden comparisons follow declared E0/E1 profile.
### 0.D Ordering and Tie-Break Policy
- Fixture and golden records sorted by `(suite_id, case_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel generation allowed; final set hash deterministic.
### 0.F Environment and Dependency Policy
- Fixture generation must run under pinned deterministic profile.
### 0.G Operator Manifest
- `Glyphser.Test.LoadFixture`
- `Glyphser.Test.ValidateGolden`
- `Glyphser.Test.UpdateGolden`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `fixtures/`, `goldens/`, `vectors/` canonical roots.
### 0.I Outputs and Metric Schema
- Outputs: `(fixture_report, golden_report)`
- Metrics: `fixtures_total`, `goldens_total`, `mismatches`
### 0.J Spec Lifecycle Governance
- Golden update policy changes are MAJOR.
### 0.K Failure and Error Semantics
- Mismatches in required E0 fields fail deterministically.
### 0.L Input/Data Provenance
- Every golden must reference fixture and schema digest.

---
## 2) System Model
### I.A Persistent State
- Fixture and golden registries.
### I.B Inputs and Hyperparameters
- Fixture payloads, expected outputs, profile metadata.
### I.C Constraints and Feasible Set
- Valid iff fixture and golden digests are present and match catalog.
### I.D Transient Variables
- compare diagnostics and update proposals.
### I.E Invariants and Assertions
- Golden updates require explicit approval mode and traceability.

---
## 3) Initialization
1. Load fixture/golden catalogs.
2. Validate digest refs.
3. Initialize deterministic compare/update pipeline.

---
## 4) Operator Manifest
- `Glyphser.Test.LoadFixture`
- `Glyphser.Test.ValidateGolden`
- `Glyphser.Test.UpdateGolden`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Test.LoadFixture`  
**Signature:** `(suite_id, case_id -> fixture_payload)`  
**Purity class:** IO  
**Determinism:** deterministic.

**Operator:** `Glyphser.Test.ValidateGolden`  
**Signature:** `(actual_output, golden_output, profile -> validate_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

**Operator:** `Glyphser.Test.UpdateGolden`  
**Signature:** `(proposal, approval_token -> update_report)`  
**Purity class:** IO  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. LoadFixture
2. ValidateGolden
3. If approved update path: UpdateGolden
4. Emit reports
```

---
## 7) Trace & Metrics
### Logging rule
- Fixture/golden operations emit deterministic records.
### Trace schema
- `run_header`: fixture_set_hash, golden_set_hash
- `iter`: suite_id, case_id, status
- `run_end`: mismatch_count, update_status
### Metric schema
- `fixtures_total`, `goldens_total`, `mismatches`
### Comparability guarantee
- Comparable iff fixture/golden sets and profile match.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- No unresolved fixture/golden digest refs.
#### VII.B Operator test vectors (mandatory)
- Load/validate/update fixtures.
#### VII.C Golden traces (mandatory)
- Golden fixture governance traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for required-field golden validation.
#### VIII.B Allowed refactor categories
- Storage/index changes preserving fixture/golden identities.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of validation outputs on frozen fixtures.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- Fixture/golden cursor and update state.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed validation/update must preserve deterministic outcomes.
