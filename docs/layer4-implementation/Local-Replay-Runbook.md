# Glyphser Local Replay Runbook
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.LocalReplayRunbook`  
**Purpose (1 sentence):** Define deterministic local replay execution steps for developers to reproduce and diagnose run divergence.  
**Spec Version:** `Glyphser.Implementation.LocalReplayRunbook` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Developer replay operations.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.LocalReplayRunbook`
- **Purpose (1 sentence):** Deterministic local replay workflow.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: minimize replay divergence count.
### 0.B Reproducibility Contract
- replay requires identical `manifest_hash`, `replay_token`, `determinism_profile_hash`.
### 0.C Numeric Policy
- binary64 for replay checks and comparator metrics.
### 0.D Ordering and Tie-Break Policy
- process trace records in canonical `(t, rank, operator_seq)` order.
### 0.E Parallel, Concurrency, and Reduction Policy
- local replay runs single-process unless distributed replay profile is explicitly enabled.
### 0.F Environment and Dependency Policy
- lockfile-pinned local runtime required.
### 0.G Operator Manifest
- `Glyphser.Replay.LoadArtifacts`
- `Glyphser.Replay.RunDeterministicReplay`
- `Glyphser.Replay.CompareOutputs`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- all operators under `Glyphser.Replay.*`.
### 0.I Outputs and Metric Schema
- outputs: `(replay_report, divergence_report)`.
### 0.J Spec Lifecycle Governance
- comparator key changes are MAJOR.
### 0.K Failure and Error Semantics
- failures emit deterministic replay error record.
### 0.L Input/Data Provenance
- replay inputs are content-addressed artifacts from checkpoint/trace/certificate.

---
## 2) System Model
### I.A Persistent State
- replay cursor, divergence accumulator, diagnostics context.
### I.B Inputs and Hyperparameters
- run id, artifact paths, replay mode (`STRICT_E0` / `TOLERANT_E1`).
### I.C Constraints and Feasible Set
- artifacts must share same `replay_token`.
### I.D Transient Variables
- per-step comparison deltas.
### I.E Invariants and Assertions
- monotonic replay step progression.

---
## 3) Initialization
1. Load manifest/checkpoint/trace/certificate references.
2. Validate hash/link consistency.
3. Initialize replay comparator state.

---
## 4) Operator Manifest
- `Glyphser.Replay.LoadArtifacts`
- `Glyphser.Replay.RunDeterministicReplay`
- `Glyphser.Replay.CompareOutputs`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Replay.LoadArtifacts`  
**Signature:** `(artifact_refs -> replay_inputs)`  
**Purity class:** IO  
**Definition:** Loads and validates artifact hash links required for replay.

**Operator:** `Glyphser.Replay.RunDeterministicReplay`
**Signature:** `(replay_inputs -> observed_outputs, replay_report)`
**Purity class:** IO
**Definition:** Replays run steps deterministically under the active replay mode and emits canonical replay report.

**Operator:** `Glyphser.Replay.CompareOutputs`  
**Signature:** `(expected, observed, replay_mode -> diff)`  
**Purity class:** PURE  
**Definition:** Applies E0/E1 comparator rules and emits deterministic diff.

---
## 6) Procedure
```text
1. replay_inputs <- LoadArtifacts(...)
2. observed <- RunDeterministicReplay(replay_inputs)
3. diff <- CompareOutputs(expected, observed, replay_mode)
4. if diff.has_divergence: Error.Emit(REPLAY_DIVERGENCE)
5. return (replay_report, divergence_report)
```

---
## 7) Trace & Metrics
- Metrics: `divergence_count`, `first_divergence_t`, `max_abs_error`, `max_rel_error`.
- Trace includes replay mode and comparator profile hash.

---
## 8) Validation
- Golden replays for one E0 and one E1 profile.
- Fault-injected replay for deterministic divergence detection.

---
## 9) Refactor & Equivalence
- E0 for replay verdict and first divergence location.
- E1 allowed only for declared tolerant metrics.

---
## 10) Checkpoint/Restore
- Replay session checkpoint stores replay cursor and diff accumulator.
- Restore must resume with identical comparator output.
