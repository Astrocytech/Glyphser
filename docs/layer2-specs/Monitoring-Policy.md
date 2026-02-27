# Glyphser Monitoring Policy Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Monitoring.Policy`  
**Purpose (1 sentence):** Define deterministic monitoring, drift detection, and alert policy with privacy-safe telemetry contracts.  
**Spec Version:** `Glyphser.Monitoring.Policy` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Production monitoring and drift governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Monitoring.Policy`
- **Purpose (1 sentence):** Deterministic monitoring/alerting contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize undetected drift and unsafe inference behavior.
### 0.B Reproducibility Contract
- Replayable given `(monitor_policy_hash, telemetry_window_hash)`.
### 0.C Numeric Policy
- Aggregations in binary64 with deterministic windows.
### 0.D Ordering and Tie-Break Policy
- Event ordering by `(window_start, operator_seq, rank)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel telemetry streams merged by deterministic key order.
### 0.F Environment and Dependency Policy
- Telemetry must satisfy privacy classification/redaction policy.
### 0.G Operator Manifest
- `Glyphser.Monitor.Register`
- `Glyphser.Monitor.Emit`
- `Glyphser.Monitor.DriftCompute`
- `Glyphser.Monitor.AlertCreate`
- `Glyphser.Monitor.AlertAck`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Monitor.*` namespace.
### 0.I Outputs and Metric Schema
- Outputs: `(monitor_report, alert_stream)`
- Metrics: `drift_score`, `alert_count`
### 0.J Spec Lifecycle Governance
- policy threshold/metric semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- deterministic failures on invalid telemetry schema/policy.
### 0.L Input/Data Provenance
- telemetry payloads must include run_id, model_version_id, tenant_id.

---
### 0.Z EQC Mandatory Declarations Addendum
- Seed space: `seed ∈ {0..2^64-1}` when stochastic sub-operators are used.
- PRNG family: `Philox4x32-10` for declared stochastic operators.
- Randomness locality: all sampling occurs only inside declared stochastic operators in section 5.
- Replay guarantee: replayable given (seed, PRNG family, numeric policy, ordering policy, parallel policy, environment policy).
- Replay token: deterministic per-run token contribution is defined and included in trace records.
- Floating-point format: IEEE-754 binary64 unless explicitly declared otherwise.
- Rounding mode: round-to-nearest ties-to-even unless explicitly overridden.
- Fast-math policy: forbidden for critical checks and verdict paths.
- Named tolerances: `EPS_EQ=1e-10`, `EPS_DENOM=1e-12`, and domain-specific thresholds as declared.
- NaN/Inf policy: invalid values trigger deterministic failure handling per 0.K.
- Normalized exponentials: stable log-sum-exp required when exponential paths are used (otherwise N/A).
- Overflow/underflow: explicit abort or clamp behavior must be declared (this contract uses deterministic abort on critical paths).
- Approx-equality: `a ≈ b` iff `|a-b| <= EPS_EQ` when tolerance checks apply.
- Transcendental functions policy: deterministic implementation requirements are inherited from consuming operators.
- Reference runtime class: CPU-only/GPU-enabled/distributed as required by the consuming workflow.
- Compiler/flags: deterministic compilation; fast-math disabled for critical paths.
- Dependency manifest: pinned runtime dependencies and versions are required.
- Determinism level: `BITWISE` for contract-critical outputs unless a stricter local declaration exists.
- Error trace rule: final failure record includes `t`, `failure_code`, `failure_operator`, replay token, and minimal diagnostics.
- Recovery policy: none unless explicitly declared; default is deterministic abort-only.

## 2) System Model
### I.A Persistent State
- monitor definitions, alert state, drift baselines.
### I.B Inputs and Hyperparameters
- telemetry stream, policy thresholds, window params.
### I.C Constraints and Feasible Set
- privacy-unsafe telemetry rejected.
### I.D Transient Variables
- per-window aggregates and drift diagnostics.
### I.E Invariants and Assertions
- no raw features/gradients/identifiers in emitted monitoring events.

### II.F Drift Algorithm Suite (Normative)
- `drift_algorithm_id = "PSI_KS_V1"`.
- Inputs:
  - baseline sample and current-window sample over the same feature projection.
  - fixed bin edges computed deterministically from baseline quantiles (10 bins, nearest-rank quantile rule).
  - quantile cutpoints are `p ∈ {0.1, 0.2, ..., 0.9}` with index `k = floor(p * (n-1))` over baseline sorted ascending.
  - duplicate-cutpoint rule: when repeated baseline values produce non-unique cutpoints, use deterministic merged bins on distinct ascending edges; if distinct values < requested bins, reduce bin count deterministically to distinct-value count.
  - baseline is selected from monitor state by `baseline_ref` declared in monitor policy (fixed reference window hash).
  - if `baseline_ref` cannot be resolved to a valid baseline artifact/window, abort deterministically with `BASELINE_MISSING`.
- Metrics:
  - PSI on binned distributions with zero-probability guard `EPS_DENOM`:
    - `PSI = Σ_i (p_i - q_i) * ln((p_i + EPS_DENOM)/(q_i + EPS_DENOM))`.
  - KS statistic on empirical CDFs:
    - `KS = max_x |F_baseline(x) - F_current(x)|`,
    - ties are resolved by stable ascending tuple order `(value, source_rank, sample_index)` where `source_rank=0` for baseline and `1` for current.
- Missingness/NaN handling:
  - `NaN`/missing values map to dedicated `MISSING` bin; included in PSI and KS counts.
- Output:
  - `drift_score = max(psi_score, ks_score)`.
  - `drift_report` includes `{drift_algorithm_id, drift_algorithm_version, psi_score, ks_score, drift_score, window_id}`.
- Reproducibility:
  - `binning_rule = "quantile_10_bins"`.
  - `nan_rule = "separate_bin"`.
  - `drift_algorithm_hash = SHA-256(CBOR_CANONICAL([drift_algorithm_id, [drift_algorithm_version, binning_rule, nan_rule]]))`.

### II.G Auditable Policy Transcript (Normative)
- Policy evaluation must emit deterministic transcript entries:
  - `policy_input_hashes`, `rule_id`, `threshold_id`, `verdict`, `reason_code`.
- Transcript ordering rule (normative):
  - sort entries by `(window_id, rule_id, threshold_id, metric_name)`.
- Transcript hash:
  - `policy_gate_hash = SHA-256(CBOR_CANONICAL(["monitor_gate", [monitor_policy_hash, ordered_transcript_entries]]))`.
- `policy_gate_hash` must be emitted as a mandatory trace field and bound to execution certificate evidence in regulated modes.
- Network calls are forbidden during policy verdict evaluation unless all external inputs are pre-committed by hash.

### II.H Telemetry Window Commitment (Normative)
- `telemetry_window_hash = SHA-256(CBOR_CANONICAL(["telemetry_window", [window_id, start_t, end_t, aggregation_rules_hash, filter_hash]]))`.
- Monitoring transcripts and gate verdicts must reference `telemetry_window_hash` for every evaluated window.
- Alert ID rule: `alert_id = SHA-256(CBOR_CANONICAL(["alert", [drift_report, threshold_policy]]))`.
- Alert lifecycle state machine (normative): `OPEN -> ACKNOWLEDGED -> RESOLVED` with deterministic transition validation.
  - Allowed transitions only:
    - `OPEN -> ACKNOWLEDGED` (explicit acknowledgement),
    - `ACKNOWLEDGED -> RESOLVED` (condition cleared),
  - `RESOLVED` is terminal.
  - Any other transition is deterministic failure (`INVALID_STATE_TRANSITION`).

---
## 3) Initialization
1. Load monitor policy.
2. Validate telemetry schemas.
3. Initialize deterministic windows.

---
## 4) Operator Manifest
- `Glyphser.Monitor.Register`
- `Glyphser.Monitor.Emit`
- `Glyphser.Monitor.DriftCompute`
- `Glyphser.Monitor.AlertCreate`
- `Glyphser.Monitor.AlertAck`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Monitor.Register`  
**Category:** Monitoring  
**Signature:** `(monitor_policy, telemetry_schema -> registration_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** registers monitored metrics, windows, and thresholds under canonical policy hash.

**Operator:** `Glyphser.Monitor.Emit`  
**Category:** Monitoring  
**Signature:** `(monitor_event -> ok)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** appends typed `MonitorEvent` to the deterministic telemetry stream.

**Operator:** `Glyphser.Monitor.DriftCompute`  
**Category:** Monitoring  
**Signature:** `(windowed_metrics, baseline -> drift_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes drift metrics under fixed deterministic aggregation windows; missing/corrupt baseline is a deterministic failure (`BASELINE_MISSING`).

**Operator:** `Glyphser.Monitor.AlertCreate`  
**Category:** Monitoring  
**Signature:** `(drift_report, threshold_policy -> alert_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** emits deterministic alert when threshold policy is breached.

**Operator:** `Glyphser.Monitor.AlertAck`  
**Category:** Monitoring  
**Signature:** `(alert_id, principal_id, ack_reason -> ack_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** appends deterministic acknowledgement state transition for an existing alert (`OPEN -> ACKNOWLEDGED` only).

---
## 6) Procedure
```text
1. MonitorRegister
2. MonitorEmit (stream)
3. DriftCompute (window)
4. AlertCreate / AlertAck
```

---
## 7) Trace & Metrics
### Logging rule
- monitoring pipeline emits deterministic `MonitorEvent` records (schema from `docs/layer1-foundation/Data-Structures.md`) and optional linked trace entries.
### Trace schema
- `run_header`: monitor_policy_hash, tenant_id
- `iter`: `MonitorEvent`-compatible fields (`window_id`, `metric_name`, `metric_value`) plus optional `alert_state`
- `run_end`: monitor_summary_hash, policy_gate_hash
### Metric schema
- `drift_score`, `alert_count`, `false_positive_rate`
### Comparability guarantee
- Comparable iff policy hash, windowing, and `MonitorEvent` schema are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- telemetry fields typed, privacy-classed, and bounded.
#### VII.B Operator test vectors (mandatory)
- stable window aggregation, drift threshold crossings, alert transitions.
#### VII.C Golden traces (mandatory)
- golden monitoring traces for reference workloads.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for alert decisions and drift metrics on frozen telemetry.
#### VIII.B Allowed refactor categories
- pipeline scaling optimizations preserving window semantics.
#### VIII.C Equivalence test procedure (mandatory)
- compare window metrics + alert events exactly.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- monitor window cursors + alert states.
### Serialization
- deterministic CBOR.
### Restore semantics
- restored monitoring continues with identical window boundaries and alerts.

---
## 11) Policy Transcript Viewer Projection (Normative)
- In addition to hash commitments, policy-gate evaluation MUST expose a deterministic human-readable projection:
  - ordered rule evaluations,
  - input metric snapshots (redacted as required),
  - per-rule decision reason codes,
  - final pass/fail rationale.
- Viewer projection is informational but deterministic:
  - identical policy transcript input yields byte-identical viewer output.
- Projection hash:
  - `policy_transcript_view_hash = SHA-256(CBOR_CANONICAL(policy_transcript_view))`.

---
## 12) Telemetry Standards Compatibility Policy (Normative)
- Prometheus/OpenMetrics naming rules:
  - metric names MUST be lowercase snake_case with stable unit suffixes.
  - tenant/profile labels MUST use fixed canonical keys.
- OpenTelemetry mapping rules:
  - resource attributes MUST include `tenant_id`, `run_id`, `profile_id`, `env_manifest_hash`.
  - span/log identity fields MUST be deterministically derived from trace records.
- Upgrade compatibility requirement:
  - telemetry field renames/removals require a compatibility mapping table and one deprecation window.
