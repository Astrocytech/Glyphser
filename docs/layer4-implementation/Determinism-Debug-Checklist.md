# Glyphser Determinism Debug Checklist
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.DeterminismDebugChecklist`  
**Purpose (1 sentence):** Define deterministic debugging workflow to localize and resolve replay divergence sources across data, model, DP, backend, and runtime layers.  
**Spec Version:** `Glyphser.Implementation.DeterminismDebugChecklist` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Replay debugging and incident triage.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.DeterminismDebugChecklist`
- **Purpose (1 sentence):** Deterministic divergence triage.
### 0.A Objective Semantics
- minimize time-to-root-cause for determinism failures.
### 0.B Reproducibility Contract
- checklist verdict reproducible from artifacts and profile hash.
### 0.C Numeric Policy
- comparator math in binary64.
### 0.D Ordering and Tie-Break Policy
- triage sequence fixed: config -> data -> RNG -> backend -> DP -> model.
### 0.E Parallel, Concurrency, and Reduction Policy
- checks may run parallel, findings merged in fixed order.
### 0.F Environment and Dependency Policy
- must compare lockfile + env manifest before other checks.
### 0.G Operator Manifest
- `Glyphser.Replay.CheckArtifactLinkage`
- `Glyphser.Replay.CheckRNGProgression`
- `Glyphser.Replay.CheckBackendProfile`
- `Glyphser.Replay.LocalizeFirstDivergence`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- replay/debug operators under `Glyphser.Replay.*`.
### 0.I Outputs and Metric Schema
- `(debug_report, root_cause, remediation_actions)`.
### 0.J Spec Lifecycle Governance
- checklist ordering changes are MINOR; acceptance criteria changes MAJOR.
### 0.K Failure and Error Semantics
- inability to localize emits deterministic fallback code.
### 0.L Input/Data Provenance
- uses run artifacts and trace chain.

---
## 2) System Model
### I.A Persistent State
- debug session state and finding registry.
### I.B Inputs and Hyperparameters
- baseline run refs, candidate run refs, replay mode.
### I.C Constraints and Feasible Set
- both runs must be artifact-complete.
### I.D Transient Variables
- per-stage check results.
### I.E Invariants and Assertions
- first divergence index monotonic once found.

---
## 3) Initialization
1. Load evidence bundles.
2. Verify shared schema versions.
3. Initialize check pipeline.

---
## 4) Operator Manifest
- `Glyphser.Replay.CheckArtifactLinkage`
- `Glyphser.Replay.CheckRNGProgression`
- `Glyphser.Replay.CheckBackendProfile`
- `Glyphser.Replay.LocalizeFirstDivergence`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Replay.CheckArtifactLinkage`  
**Signature:** `(baseline_refs, candidate_refs -> linkage_report)`  
**Purity class:** PURE  
**Definition:** Verifies hash-chain and artifact binding coherence.

**Operator:** `Glyphser.Replay.CheckRNGProgression`
**Signature:** `(baseline_trace, candidate_trace, replay_token -> rng_progression_report)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Validates RNG offset progression and stream ownership invariants across runs under identical replay context.

**Operator:** `Glyphser.Replay.CheckBackendProfile`
**Signature:** `(baseline_runtime_profile, candidate_runtime_profile, determinism_profile_hash -> backend_profile_report)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Compares backend/runtime determinism profile bindings and emits deterministic compatibility verdict.

**Operator:** `Glyphser.Replay.LocalizeFirstDivergence`  
**Signature:** `(trace_a, trace_b -> divergence_location)`  
**Purity class:** PURE  
**Definition:** Finds first mismatched record by comparator profile.

---
## 6) Procedure
```text
1. linkage <- CheckArtifactLinkage(...)      # config/data linkage stage
2. rng_check <- CheckRNGProgression(...)     # RNG stage
3. backend_check <- CheckBackendProfile(...) # backend stage
4. loc <- LocalizeFirstDivergence(linkage, rng_check, backend_check, ...)
5. return debug_report with deterministic remediation ordering
```

---
## 7) Trace & Metrics
- Metrics: `first_divergence_t`, `first_divergence_operator`, `failed_checks_count`.
- Trace logs each checklist stage result.

---
## 8) Validation
- golden divergence cases for data/RNG/backend/DP.
- deterministic root-cause ranking test.

---
## 9) Refactor & Equivalence
- E0 for root-cause category and first divergence location.

---
## 10) Checkpoint/Restore
- debug checkpoint includes completed stage ids and localized divergence cursor.
