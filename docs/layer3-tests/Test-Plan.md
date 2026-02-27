# Glyphser Validation and Test Plan
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.TestPlanOrchestrator`  
**Purpose (1 sentence):** Execute deterministic validation suites that certify EQC invariants, operator behavior, and replay correctness.  
**Spec Version:** `Glyphser.Implementation.TestPlanOrchestrator` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Deterministic verification and regression control.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.TestPlanOrchestrator`
- **Purpose (1 sentence):** Deterministic test orchestration.
- **Spec Version:** `Glyphser.Implementation.TestPlanOrchestrator` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Reproducible validation execution.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE` failures.
- Objective type: `Scalar` (`failed_tests`).
- Comparison: fewer failures is better; ties by lower p95 regression.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` for stochastic tests.
- PRNG family: Philox4x32-10.
- Randomness locality: only stochastic test operators.
- Replay guarantee: replayable given `(test_manifest_hash, seed_set, runtime_env_hash)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.

### 0.C Numeric Policy
- Critical verdicts are boolean/integer exact.
- Performance thresholds use binary64 comparisons.
- Approx-equality: threshold-defined tolerance for performance metrics.

### 0.D Ordering and Tie-Break Policy
- Test order is deterministic by suite then test_id.
- Tie-break for flaky-equivalent outcomes: lowest test_id.

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel test execution allowed only with deterministic merge of reports.
- Aggregate counts reduced in deterministic order.

### 0.F Environment and Dependency Policy
- Reference runtime: pinned CI image.
- Determinism level: `BITWISE` for pass/fail reports; `TOLERANCE` for perf metrics.

### 0.G Operator Manifest
- `Glyphser.Test.RunUnitSuite`
- `Glyphser.Test.RunIntegrationSuite`
- `Glyphser.Test.RunGoldenTraceSuite`
- `Glyphser.Test.RunReplaySuite`
- `Glyphser.Test.AggregateResults`
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- Fully-qualified test operators required.

### 0.I Outputs and Metric Schema
- Outputs: `(test_report, verdict)`.
- Metrics: `passed`, `failed`, `skipped`, `p95_regression`, `determinism_failures`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Threshold/policy changes require version bump and migration note.

### 0.K Failure and Error Semantics
- Abort-only on infrastructure failures; per-test failures recorded deterministically.

### 0.L Input/Data Provenance
- Test fixtures and golden traces must be hash-addressed.

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
- `test_registry`, `golden_registry`.

### I.B Inputs and Hyperparameters
- suites, thresholds, seed sets, environment metadata.

### I.C Constraints and Feasible Set
- Unconstrained; validity determined by threshold policies.

### I.D Transient Variables
- per-suite reports, aggregate counters.

### I.E Invariants and Assertions
- deterministic ordering and complete report emission.

### II.F Test Manifest and Golden Inventory (Concrete)
- Test manifest required fields:
  - `manifest_version:string`
  - `suites:array<string>`
  - `seed_set:array<uint64>`
  - `thresholds:object`
  - `golden_ids:array<string>`
- Golden inventory (minimum):
  - `golden_kernel_train` -> `sha256:aa01aa01aa01aa01aa01aa01aa01aa01aa01aa01aa01aa01aa01aa01aa01aa01`
  - `golden_data_nextbatch` -> `sha256:bb02bb02bb02bb02bb02bb02bb02bb02bb02bb02bb02bb02bb02bb02bb02bb02`
  - `golden_modelir_exec` -> `sha256:cc03cc03cc03cc03cc03cc03cc03cc03cc03cc03cc03cc03cc03cc03cc03cc03`
  - `golden_dp_apply` -> `sha256:dd04dd04dd04dd04dd04dd04dd04dd04dd04dd04dd04dd04dd04dd04dd04dd04`
- Deterministic pass/fail rule: pass iff all required suites pass and no E0 field mismatch against referenced golden IDs.
- Required hardening suites:
  - property/fuzz tests for IR validation, schema parsing, checkpoint decode, and TMMU planner invariants,
  - distributed chaos tests (rank loss, network partition, delayed collective),
  - replay divergence minimization tests at scale (multi-rank long-horizon).

### II.G Property Invariants (Normative)
- IR invariants: DAG acyclic, edge typing valid, shape constraints satisfied, gradient dependency graph consistent.
- Schema invariants: normalization idempotent, unknown key handling follows `schema_mode`.
- TMMU invariants: no overlap on reused live intervals, alias/in-place constraints enforced, replan triggers deterministic.
- DP invariants: epsilon monotonicity, delta bounds respected, no negative budgets, stable accountant state hash under replay.

### II.H Fuzz Harness Inventory (Normative)
- Manifest parser fuzzer (`max_input_bytes` declared, crash=fail).
- IR ingestion fuzzer (`max_nodes` declared, crash=fail).
- Checkpoint loader fuzzer (`max_blob_bytes` declared, crash=fail).
- Trace parser fuzzer (`max_record_bytes` declared, crash=fail).
- Sanitizer baseline: memory/UB sanitizers required in fuzz CI profile.

### II.I Registry Completeness Lint (Normative)
- Parse all docs for `Failure codes:` and `allowed_error_codes`.
- Fail build if any referenced code is absent from `docs/layer1-foundation/Error-Codes.md`.

### II.J Determinism Regression Matrix (Normative)
- Required replay matrices:
  - same machine / same driver (E0 required),
  - same GPU class / different driver patch (E1 policy),
  - cross-GPU class (E1 only, explicit tolerances).
- Pass/fail policy:
  - E0 fields must be bitwise equal.
  - E1 fields must remain within declared per-field tolerance bands.

### II.K Spec Lint Gate (Normative)
- `tools/spec_lint.py` is a mandatory pre-test CI gate and must run before unit/integration/replay/performance suites.
- `spec_lint` must verify at minimum:
  - operator reference completeness across kernel/orchestrator/reference docs against canonical operator registry artifact,
  - interface digest completeness (`request_schema_digest`, `response_schema_digest`, `signature_digest`, `side_effects`, `allowed_error_codes`, `required_capabilities`),
  - error-code closure (all referenced codes must exist in `docs/layer1-foundation/Error-Codes.md` with valid severity enum),
  - no placeholder digests in normative fields (must be 64-hex where declared),
  - contract-critical hash primitive and domain-separation consistency.
- CI must fail deterministically on any `spec_lint` violation before running other suites.

---

## 3) Initialization

1. Load test manifest.
2. Validate fixture hashes.
3. Initialize deterministic run order.

---

## 4) Operator Manifest

- `Glyphser.Test.RunUnitSuite`
- `Glyphser.Test.RunIntegrationSuite`
- `Glyphser.Test.RunGoldenTraceSuite`
- `Glyphser.Test.RunReplaySuite`
- `Glyphser.Test.AggregateResults`
- `Glyphser.Error.Emit`

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

**Operator:** `Glyphser.Test.RunUnitSuite`  
**Category:** IO  
**Signature:** `(suite_config -> suite_report)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** executes ordered unit tests and records outcomes.  
**Preconditions / Postconditions:** fixtures available.  
**Edge cases:** skipped tests.  
**Numerical considerations:** threshold comparisons in binary64 where needed.  
**Ordering/tie handling:** test_id ascending.  
**Complexity note:** O(number_of_tests).  
**Failure behavior:** deterministic failure logs.  
**Dependencies:** test runner backend.  
**Test vectors:** synthetic pass/fail suites.

**Operator:** `Glyphser.Test.RunGoldenTraceSuite`  
**Category:** IO  
**Signature:** `(golden_config -> golden_report)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** compares produced traces against golden references.  
**Preconditions / Postconditions:** golden artifacts present.  
**Edge cases:** missing optional trace fields.  
**Numerical considerations:** exact for E0 fields; tolerance for E1 fields.  
**Ordering/tie handling:** trace step order strict.  
**Complexity note:** O(trace_size).  
**Failure behavior:** deterministic mismatch reports.  
**Dependencies:** trace comparator.  
**Test vectors:** known golden mismatch/pass cases.

**Operator:** `Glyphser.Test.AggregateResults`  
**Category:** IO  
**Signature:** `(suite_reports -> test_report, verdict)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** deterministic aggregation and verdict computation.  
**Preconditions / Postconditions:** all suite reports available.  
**Edge cases:** empty suite set.  
**Numerical considerations:** deterministic reduction order.  
**Ordering/tie handling:** suite-name lexical merge.  
**Complexity note:** O(total_cases).  
**Failure behavior:** abort on malformed report.  
**Dependencies:** suite schemas.  
**Test vectors:** aggregate snapshots.

---

**Operator:** `Glyphser.Test.RunIntegrationSuite`  
**Category:** Test  
**Signature:** `(integration_manifest -> integration_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Executes deterministic integration scenarios across kernel, data, model, memory, and DP boundaries.
**Preconditions / Postconditions:** integration fixtures and dependency contracts are available; output report includes per-scenario status and hashes.  
**Edge cases:** optional components disabled by profile.  
**Numerical considerations:** E0 fields exact; E1 metrics use declared tolerances only.  
**Ordering/tie handling:** scenario_id ascending deterministic execution.  
**Complexity note:** O(number_of_integration_scenarios).  
**Failure behavior:** abort on malformed integration manifest; otherwise deterministic failure records in report.  
**Dependencies:** kernel/component contracts and trace schema.  
**Test vectors:** mixed pass/fail integration matrices.
`integration_manifest` schema (normative): `{suite_id:string, scenarios:array<string>, fixtures_hash:bytes32, comparison_profile:object}`.

**Operator:** `Glyphser.Test.RunReplaySuite`  
**Category:** Test  
**Signature:** `(replay_manifest -> replay_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Validates replay-token determinism, RNG locality, and checkpoint-restore replay guarantees.
**Preconditions / Postconditions:** replay traces/checkpoints and token definitions are available; output report includes replay equivalence verdicts.  
**Edge cases:** missing intermediate checkpoint segments.  
**Numerical considerations:** replay-critical comparisons are bitwise for E0 fields.  
**Ordering/tie handling:** replay-case order is deterministic by replay_case_id ascending.  
**Complexity note:** O(total_replayed_steps).  
**Failure behavior:** abort on invalid replay manifest; deterministic mismatch reports otherwise.  
**Dependencies:** Replay-Determinism and Checkpoint-Schema contracts.  
**Test vectors:** fixed-token replay pass/mismatch scenarios.

## 6) Procedure

```text
1. RunUnitSuite(suite_config)
2. RunIntegrationSuite(integration_manifest)
3. RunGoldenTraceSuite(golden_config)
4. RunReplaySuite(replay_manifest)
5. AggregateResults(suite_reports)
6. Return report + verdict
```

---

## 7) Trace & Metrics

### Logging rule
Every executed test emits deterministic result records.

### Trace schema
- `run_header`: manifest_hash, runtime_env_hash, replay_token
- `iter`: suite, test_id, result
- `run_end`: verdict, aggregate counts

### Metric schema
- `passed`, `failed`, `skipped`, `p95_regression`, `determinism_failures`

### Comparability guarantee
Comparable iff same suites, fixtures, thresholds, and merge policy.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Covers symbol completeness, no hidden globals, deterministic order, trace compliance.
- Namespace hygiene rule: fail if any operator token matches flat form `Glyphser\\.[A-Za-z0-9_]+_v\\d+`; only `Glyphser.<subsystem>.<name>_v<integer>` is allowed.

#### VII.B Operator test vectors (mandatory)
Includes suite-runner and aggregator vectors.
Includes orchestrator idempotency vectors: duplicate dispatch/ack events must commit exactly once and return the same transition record for identical `idempotency_key`.
Includes deterministic fault-injection recovery vectors:
- crash after trace write but before checkpoint,
- crash after checkpoint write but before certificate,
- duplicate dispatch/retry storms,
- partial shard write and interrupted commit.
Each fault-injection vector must assert deterministic recovery, exactly-once visible commit semantics, and certificate/artifact hash coherence.

#### VII.C Golden traces (mandatory)
Golden report snapshots for canonical test manifests.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 for verdict and aggregate counters.

#### VIII.B Allowed refactor categories
- Runner implementation changes preserving outputs.

#### VIII.C Equivalence test procedure (mandatory)
Exact report diff against golden baseline.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- partial suite reports and deterministic run cursor.

### Serialization
- deterministic canonical CBOR.

### Restore semantics
- resume yields identical final report and verdict.
