# Glyphser Storage Recovery Test Matrix
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.StorageRecoveryMatrix`  
**Purpose (1 sentence):** Define deterministic storage crash-recovery tests for WAL segments, commit pointers, and artifact integrity.  
**Spec Version:** `Glyphser.Test.StorageRecoveryMatrix` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Storage reliability testing.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.StorageRecoveryMatrix`
- **Purpose (1 sentence):** Deterministic storage recovery test contract.
### 0.A Objective Semantics
- minimize unrecoverable commit states.
### 0.B Reproducibility Contract
- scenario verdict reproducible from `(scenario_id, backend_profile_hash, fixtures_hash)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- sequence ids and counters as uint64.
### 0.D Ordering and Tie-Break Policy
- scenarios ordered by `(backend, scenario_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- scenarios parallelizable with deterministic report merge.
### 0.F Environment and Dependency Policy
- backend adapter versions pinned.
### 0.G Operator Manifest
- `Glyphser.Test.InjectStorageFault`
- `Glyphser.Test.RunRecoveryProcedure`
- `Glyphser.Test.VerifyRecoveryInvariants`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Test.*` and `Glyphser.Storage.*`.
### 0.I Outputs and Metric Schema
- outputs: `(scenario_reports, matrix_verdict)`.
### 0.J Spec Lifecycle Governance
- scenario semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- unrecoverable states are deterministic failures.
### 0.L Input/Data Provenance
- fixtures and expected results are hash-addressed.
### 0.Z EQC Mandatory Declarations Addendum
- seed space: `uint64` (for deterministic fault schedule selection).
- PRNG family: `Philox4x32-10` when stochastic scenario expansion is enabled.
- replay guarantee: identical `(scenario_id, backend_profile_hash, fixtures_hash)` yields identical scenario verdict.
- floating-point format: IEEE-754 binary64 for informational metrics only.
- NaN/Inf policy: invalid in recorded metrics.
- default tolerances: N/A for invariant pass/fail.
- determinism target: E0 for per-scenario verdict and invariant failure ids.

---
## 2) System Model
### I.A Persistent State
- scenario catalog and backend capability matrix.
### I.B Inputs and Hyperparameters
- backend id, scenario set, strictness profile, fixtures set hash (`fixtures_hash`).
### I.C Constraints and Feasible Set
- commit pointer logic required for all backends.
### I.D Transient Variables
- injected fault records and recovery outputs.
### I.E Invariants and Assertions
- committed runs must remain verifiable after recovery.

---
## 3) Initialization
1. Load scenario matrix and backend profile.
2. Initialize isolated test storage namespace.
3. Seed deterministic fault injector.

---
## 4) Operator Manifest
- `Glyphser.Test.InjectStorageFault`
- `Glyphser.Test.RunRecoveryProcedure`
- `Glyphser.Test.VerifyRecoveryInvariants`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Test.InjectStorageFault`
**Signature:** `(scenario_id, backend_id, storage_state -> faulted_storage_state)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Injects the declared deterministic storage fault for the scenario.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `SCENARIO_INVALID`, `BACKEND_UNSUPPORTED`.

**Operator:** `Glyphser.Test.RunRecoveryProcedure`
**Signature:** `(faulted_storage_state, recovery_policy -> recovery_result)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Runs deterministic recovery procedure (WAL scan/replay/rollback as declared).
**allowed_error_codes:** `CONTRACT_VIOLATION`, `RECOVERY_FAILURE`, `WAL_CORRUPTION`.

**Operator:** `Glyphser.Test.VerifyRecoveryInvariants`  
**Signature:** `(recovery_result, expected_invariants -> verdict)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Verifies WAL chain integrity, pointer correctness, and artifact hash coherence.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `INVARIANT_VIOLATION`.

---
## 6) Procedure
```text
1. InjectStorageFault
2. RunRecoveryProcedure
3. VerifyRecoveryInvariants
4. Record scenario verdict
```

---
## 7) Trace & Metrics
- Metrics: `scenarios_total`, `scenarios_failed`, `recovery_time_ms` (informational only; excluded from deterministic verdict logic).
- Trace includes scenario id, backend id, invariant failures.

---
## 8) Validation
- baseline scenarios for local fs, s3-compatible, gcs-compatible adapters.
- deterministic fault replay tests.

---
## 9) Refactor & Equivalence
- E0 for per-scenario verdicts and invariant failure identities.

---
## 10) Checkpoint/Restore
- checkpoint stores `scenario_cursor`, `completed_scenarios[]`, `partial_matrix_report_hash`, and `backend_profile_hash`.
- restore resumes matrix deterministically.
