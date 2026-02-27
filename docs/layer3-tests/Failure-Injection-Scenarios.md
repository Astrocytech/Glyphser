# Glyphser Failure Injection Scenarios Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.FailureInjection`  
**Purpose (1 sentence):** Define deterministic fault-injection scenarios and expected recovery outcomes across core runtime and governance paths.  
**Spec Version:** `Glyphser.Test.FailureInjection` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Resilience and recovery verification.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.FailureInjection`
- **Purpose (1 sentence):** Deterministic fault-injection contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: verify deterministic recovery under defined fault classes.
### 0.B Reproducibility Contract
- Replayable given `(scenario_id, injection_point, seed, evidence_bundle_hash)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- Scenario timing and counters use exact deterministic tick values.
### 0.D Ordering and Tie-Break Policy
- Injection sequence order is fixed by scenario definition.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-fault scenarios allowed only when deterministic ordering is declared.
### 0.F Environment and Dependency Policy
- Faults must not alter contract definitions; only runtime behavior under test.
### 0.G Operator Manifest
- `Glyphser.Test.InjectFault`
- `Glyphser.Test.RunRecovery`
- `Glyphser.Test.ValidateRecoveryOutcome`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `tests/failure_injection/` suites.
### 0.I Outputs and Metric Schema
- Outputs: `(fault_report, recovery_verdict)`
- Metrics: `scenarios_total`, `recovery_passed`, `recovery_failed`
### 0.J Spec Lifecycle Governance
- Required scenario set changes are MAJOR.
### 0.K Failure and Error Semantics
- Unexpected recovery outcomes are deterministic failures.
### 0.L Input/Data Provenance
- Scenario definitions and expected outcomes must be hash-addressed.
### 0.Z EQC Mandatory Declarations Addendum
- seed space: `uint64`.
- PRNG family: `Philox4x32-10` for stochastic fault payload generation.
- replay guarantee: identical `(scenario_id, injection_point, seed, evidence_bundle_hash, runtime_profile)` yields identical `(fault_report, recovery_verdict)`.
- floating-point format: IEEE-754 binary64 for informational metrics only.
- NaN/Inf policy: invalid in recorded metrics.
- default tolerances: N/A for pass/fail recovery verdicts.
- determinism target: E0 for `recovery_verdict` and evidence identities.

---
## 2) System Model
### I.A Persistent State
- Scenario registry and expected recovery matrix.
### I.B Inputs and Hyperparameters
- scenario id, fault point, `seed`, runtime profile, and evidence bundle (with `evidence_bundle_hash` commitment).
### I.C Constraints and Feasible Set
- Valid iff scenario has declared expected deterministic outcome.
### I.D Transient Variables
- injection logs and recovery diagnostics.
### I.E Invariants and Assertions
- First divergence and final verdict must be deterministic.

### II.F Mandatory Chaos Scenarios and Recovery Proof Packs (Normative)
- Mandatory baseline chaos scenarios:
  - `network_partition_primary_quorum`
  - `artifact_store_partial_unavailable`
  - `wal_corruption_truncated_tail`
  - `wal_corruption_checksum_mismatch`
- Regulated-mode requirement:
  - each mandatory scenario MUST emit a `recovery_proof_pack`.
- Recovery proof pack minimum contents:
  - `scenario_id`,
  - injected fault descriptor hash,
  - recovery transcript hash,
  - invariant check results,
  - final recovery verdict.
- Identity rule:
  - `recovery_proof_pack_hash = SHA-256(CBOR_CANONICAL(recovery_proof_pack))`.

---
## 3) Initialization
1. Load scenario definitions.
2. Validate environment and fixture preconditions.
3. Initialize deterministic injection controller.

---
## 4) Operator Manifest
- `Glyphser.Test.InjectFault`
- `Glyphser.Test.RunRecovery`
- `Glyphser.Test.ValidateRecoveryOutcome`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Test.InjectFault`  
**Signature:** `(scenario_id, runtime_state -> faulted_state)`  
**Purity class:** IO  
**Determinism:** deterministic.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `FAULT_POINT_INVALID`.

**Operator:** `Glyphser.Test.RunRecovery`  
**Signature:** `(faulted_state, recovery_policy -> recovery_state)`  
**Purity class:** IO  
**Determinism:** deterministic.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `RECOVERY_FAILURE`.

**Operator:** `Glyphser.Test.ValidateRecoveryOutcome`  
**Signature:** `(recovery_state, expected_outcome -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `RECOVERY_OUTCOME_MISMATCH`.

---
## 6) Procedure
```text
1. InjectFault
2. RunRecovery
3. ValidateRecoveryOutcome
4. Emit fault_report
```

---
## 7) Trace & Metrics
### Logging rule
- Fault and recovery paths emit deterministic scenario records.
### Trace schema
- `run_header`: scenario_id, profile_hash
- `iter`: injection_point, status
- `run_end`: recovery_verdict, outcome_hash
### Metric schema
- `scenarios_total`, `recovery_passed`, `recovery_failed`, `recovery_time_ms` (informational only; excluded from deterministic verdict logic)
### Comparability guarantee
- Comparable iff same scenario and profile.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Every required scenario has expected deterministic outcome.
#### VII.B Operator test vectors (mandatory)
- Fault/recovery vectors for WAL, checkpoint, replay, and pipeline.
#### VII.C Golden traces (mandatory)
- Golden failure-injection traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for scenario verdict and recovery evidence hashes.
#### VIII.B Allowed refactor categories
- Harness/runtime refactors preserving outcome semantics.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of validation reports.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- `scenario_cursor`, `injection_log_hash`, `partial_recovery_diagnostics_hash`, `current_outcome_hash`.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed scenario must produce identical recovery verdict.

## 13) Failure Injection Index Reference (Normative)
- `docs/layer3-tests/Failure-Injection-Index.md` is the authoritative mapping index from mandatory scenarios to invariants, recovery procedures, and proof-pack field expectations.
