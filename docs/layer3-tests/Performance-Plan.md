# Glyphser Performance Governance
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.PerformanceGovernance`  
**Purpose (1 sentence):** Define deterministic performance measurement, thresholds, and regression-gating for core Glyphser operators.  
**Spec Version:** `Glyphser.Implementation.PerformanceGovernance` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Reproducible performance benchmarking and policy enforcement.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.PerformanceGovernance`
- **Purpose (1 sentence):** Deterministic benchmark governance.
- **Spec Version:** `Glyphser.Implementation.PerformanceGovernance` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Performance policy contract.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE` p95 latency and memory peak regressions.
- Objective type: `Vector` with deterministic lexicographic order: `(regression_failures, p95_latency_delta, memory_delta)`.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` for stochastic workloads.
- PRNG family: inherited from tested operators.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
- Randomness locality: benchmark harness does not sample except workload generation operators.
- Replay guarantee: benchmark replayable given `(workload_manifest, runtime_env_hash, seeds, commit_hash)`.
- Determinism scope: metric sampling is physical-world variable; aggregation and verdict are deterministic given a frozen metric snapshot hash.

### 0.C Numeric Policy
- Timing and memory metrics stored in binary64/integer nanoseconds and bytes.
- Quantile method: nearest-rank (`k = ceil(p*n)` on sorted ascending samples, 1-indexed); ties resolved by stable input order.
- NaN/Inf metrics are invalid and fail the run.
- Approx-equality: threshold-based comparisons.

### 0.D Ordering and Tie-Break Policy
- Benchmarks run in deterministic workload order.
- Tie-break by workload id.

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel benchmark execution allowed with deterministic metric merge order.

### 0.F Environment and Dependency Policy
- Pinned benchmark runtime image and dependency lockfile required.
- Determinism level: deterministic analysis/verdict over frozen samples (E0 on analysis), tolerance-based policy on raw metrics.

### 0.G Operator Manifest
- `Glyphser.Perf.RunBenchmark`
- `Glyphser.Perf.AggregateMetrics`
- `Glyphser.Perf.EvaluateRegressionPolicy`
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- Fully-qualified performance operators required.

### 0.I Outputs and Metric Schema
- Outputs: `(perf_report, gate_verdict, metric_snapshot_hash)`.
- Metrics: `p50`, `p95`, `p99`, `peak_memory`, `throughput`, `regression_count`, `peak_memory_bytes`, `tmmu_fragmentation_ratio`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Threshold or metric definition changes require version bump and migration notes.

### 0.K Failure and Error Semantics
- Deterministic abort on invalid benchmark artifacts.

### 0.L Input/Data Provenance
- Workloads and baselines must be hash-addressed with provenance metadata.

---

### 0.Z EQC Mandatory Declarations Addendum
- Seed space: `seed ∈ {0..2^64-1}` when stochastic sub-operators are used.
- PRNG family: inherited from tested operators (must match each operator contract’s declared PRNG family).
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
- benchmark baseline registry and threshold policy.

### I.B Inputs and Hyperparameters
- workload set, hardware profile, seeds, thresholds.

### I.C Constraints and Feasible Set
- Unconstrained; gate verdict determined by policy thresholds.

### I.D Transient Variables
- per-workload metric samples and aggregate stats.

### I.E Invariants and Assertions
- deterministic run order and complete metric emission.

### II.F Regression Guards (Normative)
- `peak_memory_bytes` ceiling is mandatory per workload/profile; exceeding ceiling is a hard failure.
- `tmmu_fragmentation_ratio` is computed deterministically as `1 - (largest_free_block_bytes / total_free_bytes)` at measurement point.
- Division-by-zero rule: if `total_free_bytes == 0`, set `tmmu_fragmentation_ratio = 1` and emit `memory_pressure_state = "EXHAUSTED"`.
- Fragmentation regression beyond declared threshold is a hard failure.
- Gate verdict is computed on frozen snapshot samples only.

### II.G Resource Ledger Gate Inputs (Normative)
- Performance gates must ingest deterministic resource-ledger counters:
  - `bytes_allocated`, `peak_bytes`, `io_bytes_read`, `io_bytes_written`, `gpu_time_ms`, `cpu_time_ms`.
- Quota policy decisions must be reproducible from frozen snapshots and bound to `quota_policy_hash`.
- Any quota overrun gate failure must emit deterministic diagnostics and failure code.

### II.H Metric Snapshot Hash (Normative)
- Benchmark verdicts must be computed from a frozen metric snapshot object:
  - `MetricSnapshot = {snapshot_id, workload_ids_sorted, samples_by_workload, warmup_discard_count, quantile_method, runtime_env_hash, baseline_hash, threshold_hash}`.
- Canonical serialization: `CBOR_CANONICAL`.
- Snapshot hash:
  - `metric_snapshot_hash = SHA-256(CBOR_CANONICAL(MetricSnapshot))`.
- Gate verdict record must include `metric_snapshot_hash`; comparisons and audits must use this hash as the authoritative metric evidence identity.

### II.I Baseline Commitment (Normative)
- `baseline_hash = SHA-256(CBOR_CANONICAL(["perf_baseline", [workload_manifest_hash, runtime_env_hash, driver_runtime_fingerprint_hash, hardware_fingerprint_hash, sample_policy_hash]]))`.
- Performance comparisons are valid only when baseline and candidate share compatible workload and environment commitment sets.

---

## 3) Initialization

1. Load baseline metrics and thresholds.
2. Validate workload manifests.
3. Initialize deterministic execution order.

---

## 4) Operator Manifest

- `Glyphser.Perf.RunBenchmark`
- `Glyphser.Perf.AggregateMetrics`
- `Glyphser.Perf.EvaluateRegressionPolicy`
- `Glyphser.Error.Emit`

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

**Operator:** `Glyphser.Perf.RunBenchmark`  
**Category:** IO  
**Signature:** `(workload, env -> metric_samples)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic under fixed env/workload seeds  
**Definition:** executes one workload and records latency/memory/throughput samples.  
**Preconditions / Postconditions:** workload/env validated.  
**Edge cases:** warmup-only short runs.  
**Numerical considerations:** metrics in ns/bytes with stable aggregators.  
**Ordering/tie handling:** deterministic sample ordering.  
**Complexity note:** workload-dependent.  
**Failure behavior:** deterministic benchmark failure record.  
**Dependencies:** benchmark harness.  
**Test vectors:** synthetic workload performance fixtures.

**Operator:** `Glyphser.Perf.AggregateMetrics`  
**Category:** IO  
**Signature:** `(metric_samples -> aggregate_metrics)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes p50/p95/p99/peaks/throughput in deterministic order using nearest-rank quantiles on stably sorted samples.  
**Preconditions / Postconditions:** sufficient samples.  
**Edge cases:** low-sample run.  
**Numerical considerations:** stable percentile computation policy.  
**Ordering/tie handling:** sorted sample values, stable tie handling.  
**Complexity note:** O(n log n).  
**Failure behavior:** abort on invalid sample values.  
**Dependencies:** percentile calculator.  
**Test vectors:** fixed sample -> fixed aggregates.

**Operator:** `Glyphser.Perf.EvaluateRegressionPolicy`  
**Category:** IO  
**Signature:** `(aggregate_metrics, baselines, thresholds -> gate_verdict)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** applies regression policy and emits pass/fail verdict.  
**Preconditions / Postconditions:** baselines exist for workload profile.  
**Edge cases:** missing baseline path.  
**Numerical considerations:** tolerance thresholds applied in binary64.  
**Ordering/tie handling:** deterministic workload merge and policy order.  
**Complexity note:** O(workloads).  
**Failure behavior:** deterministic policy failure report.  
**Dependencies:** policy config and baseline registry.  
**Test vectors:** pass/fail threshold boundary cases.

---

## 6) Procedure

```text
1. RunBenchmark for each workload
2. AggregateMetrics
3. EvaluateRegressionPolicy
4. Return perf_report + gate_verdict
```

---

## 7) Trace & Metrics

### Logging rule
Each workload emits deterministic benchmark records.

### Trace schema
- `run_header`: runtime_env_hash, baseline_hash, replay_token
- `iter`: workload_id, sample_stats
- `run_end`: aggregate_metrics, metric_snapshot_hash, gate_verdict

### Metric schema
- `p50`, `p95`, `p99`, `peak_memory`, `throughput`, `regression_count`

### Comparability guarantee
Comparable iff workloads, env, baselines, and threshold policies are identical.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes deterministic ordering, explicit thresholds, trace compliance.

#### VII.B Operator test vectors (mandatory)
Benchmark, aggregation, and policy-evaluation vectors.

#### VII.C Golden traces (mandatory)
Golden aggregate metrics for canonical workloads.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 for gate verdict and aggregate metrics under same samples.

#### VIII.B Allowed refactor categories
- harness optimization preserving metrics/verdict semantics.

#### VIII.C Equivalence test procedure (mandatory)
Compare aggregate metrics and verdicts exactly/tolerance as declared.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- partial benchmark samples and deterministic run cursor.

### Serialization
- deterministic canonical CBOR.

### Restore semantics
- resumed run yields identical aggregate metrics and verdict.

---
## 11) Performance-as-Contract Baseline Tiers (Normative)
- Official benchmark tiers:
  - `cpu_tier`
  - `single_gpu_tier`
  - `multi_gpu_tier`
- For each tier, release evidence MUST include:
  - `env_manifest_hash`,
  - ordered `workload_ids`,
  - `baseline_hash`,
  - regression gate verdict and diagnostics hash.
- Baseline identity:
  - `tier_baseline_hash = SHA-256(CBOR_CANONICAL([tier_id, [env_manifest_hash, workload_ids_sorted, baseline_metrics]]))`.
- External comparability requirement:
  - performance claims are externally valid only when tier id + environment fingerprint + workload set match.

## 13) Benchmark Evidence Specification Reference (Normative)
- `docs/layer4-implementation/Benchmark-Evidence-Spec.md` defines required benchmark evidence fields and release-gate identity bindings.
