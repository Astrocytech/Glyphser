# Glyphser Replay and Determinism Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.ReplayDeterminismContract`  
**Purpose (1 sentence):** Define and verify deterministic replay semantics, RNG ownership, token composition, and restore equivalence.  
**Spec Version:** `Glyphser.Implementation.ReplayDeterminismContract` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Reproducibility and replay verification.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.ReplayDeterminismContract`
- **Purpose (1 sentence):** Deterministic replay contract.
- **Spec Version:** `Glyphser.Implementation.ReplayDeterminismContract` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Replay verification.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE` replay divergences.
- Objective type: `Scalar` (`divergence_count`).
- Invalid policy: malformed trace/token treated as failure.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}`.
- PRNG family: Philox4x32-10.
- Randomness locality: only declared stochastic operators may draw RNG.
- Replay guarantee: replayable given `(seed, policies, runtime_env_hash, operator_versions)`.
- Replay token definitions are explicit and versioned.

### 0.C Numeric Policy
- Determinism checks for critical fields are exact.
- Tolerance checks allowed only for declared non-critical metrics.
- Approx-equality uses explicit threshold definitions.

### 0.D Ordering and Tie-Break Policy
- Trace comparison order is canonical total order `(t, rank, operator_seq)`.

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel traces are merged under the same canonical total order `(t, rank, operator_seq)`.

### 0.F Environment and Dependency Policy
- Reference runtime and dependency hash required for replay comparability.
- Determinism level: BITWISE/TOLERANCE/DISTRIBUTIONAL declared per field class.

### 0.G Operator Manifest
- `Glyphser.Replay.ComputeReplayToken`
- `Glyphser.Replay.VerifyRNGOwnership`
- `Glyphser.Replay.CompareTrace`
- `Glyphser.Replay.VerifyRestore`
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- Fully-qualified replay operator names required.

### 0.I Outputs and Metric Schema
- Outputs: `(replay_report, divergence_summary)`.
- Metrics: `divergence_count`, `first_divergence_t`, `rng_violation_count`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Replay token formula changes require MAJOR bump.

### 0.K Failure and Error Semantics
- Deterministic abort on malformed trace/hash state.

### 0.L Input/Data Provenance
- All compared traces/checkpoints must be hash-addressed.

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
- replay policy registry and token formulas.

### I.B Inputs and Hyperparameters
- trace pairs, checkpoint pairs, policy config.

### I.C Constraints and Feasible Set
- Unconstrained; validity by token/trace compatibility.

### I.D Transient Variables
- divergence records and rng counter deltas.

### I.E Invariants and Assertions
- deterministic comparator order and complete reporting.

### II.F Replay Token Formulas (Authoritative)
- `kernel_replay_token = SHA-256(CBOR_CANONICAL(["replay_token", [spec_version, policy_bundle_hash, env_manifest_hash, operator_contracts_root_hash, determinism_profile_hash, driver_runtime_fingerprint_hash, uint64(seed)]]))`.
- `env_manifest_hash` is computed per `docs/layer1-foundation/Environment-Manifest.md` (alias `runtime_env_hash` must resolve to same bytes32).
- `epoch_seed = SHA-256(CBOR_CANONICAL(["nextbatch_epoch_seed", [kernel_replay_token, manifest_hash, dataset_key, uint64(epoch)]]))[0:16]`.
- `data_replay_t = SHA-256(CBOR_CANONICAL(["nextbatch", [kernel_replay_token, dataset_key, uint64(epoch), uint64(global_position), uint32(world_size), uint32(rank)]]))`.
- `modelir_replay_t = SHA-256(CBOR_CANONICAL(["modelir_executor", [kernel_replay_token, ir_hash, mode, uint64(global_position)]]))`.
- `dp_replay_t = SHA-256(CBOR_CANONICAL(["dp_apply", [kernel_replay_token, uint64(t), dp_accountant_state_hash, allocation_mode, fused_kernel, safety_reserve]]))`.
- Required comparator keys in traces: `t`, `rank`, `operator_seq`, `operator_id`, `status`, `replay_token`, plus optional domain metrics.
- Canonical compare order is `(t, rank, operator_seq)`.
- Clarification: `data_replay_t` is a per-step trace token; sampler RNG seed source is `epoch_seed` above.
- Philox mapping (normative):
  - `epoch_seed` is 16 raw bytes.
  - `philox_key = [u32_le(epoch_seed[0:4]), u32_le(epoch_seed[4:8])]`.
  - `philox_counter_base = [u32_le(epoch_seed[8:12]), u32_le(epoch_seed[12:16]), 0, 0]`.
  - All `u32_le` conversions are little-endian, unsigned.
- Counter advancement is deterministic and tracked by `rng_offset_before/after`.
  - counter increment rule: each RNG draw increments the 128-bit counter by 1 (little-endian word carry propagation across four u32 words).
- Required environment capture in replay token context:
  - driver/runtime versions,
  - determinism-affecting env vars (e.g., TF32 toggles, deterministic kernel flags, collective ordering flags),
  - backend adapter build hash.
- `DriverRuntimeFingerprint` schema and hash:
  - schema fields: `gpu_model`, `gpu_sm_count`, `driver_version`, `cuda_version`, `cudnn_version`, `cublas_version`, `nccl_version`, `os_kernel_version`, `compiler_id`, `compiler_flags_hash`, `backend_adapter_version`, `backend_build_id`.
  - `driver_runtime_fingerprint_hash = SHA-256(CBOR_CANONICAL(driver_runtime_fingerprint_map))`.
  - field-order requirement: keys MUST appear exactly in the listed order for canonical map construction.
- Replay token minimum state coverage:
  - Operator contracts: `operator_contracts_root_hash`,
  - RNG counters: `rng_offset_before`, `rng_offset_after`,
  - DP: `dp_accountant_state_hash`, `dp_config_hash`,
  - Data: `sampler_config_hash`, `effective_q`,
  - Memory: `tmmu_plan_hash`,
  - Backend: `backend_binary_hash`, `determinism_profile_hash`, `driver_runtime_fingerprint_hash`.
- Supply chain: `lockfile_hash`, `toolchain_hash`, `dependencies_lock_hash`.

### II.G DeterminismProfile (Normative)
- `tf32: bool`
- `allowlist_cublas_algorithms: array<string>`
- `allowlist_cudnn_algorithms: array<string>`
- `reduction_ordering: enum("ASCENDING_INDEX","ASCENDING_RANK_RING")`
- `atomic_reductions_allowed: bool` (`false` required for E0)
- `env_vars_fingerprint: bytes32`
  - computed as `SHA-256(CBOR_CANONICAL(sorted([(name,value)])))` over determinism-critical environment allowlist:
    - `CUBLAS_WORKSPACE_CONFIG`, `CUDA_VISIBLE_DEVICES`, `NCCL_ALGO`, `NCCL_PROTO`, `OMP_NUM_THREADS`, `PYTHONHASHSEED`.
  - inclusion rule: include only variables that are actually set; resulting `(name,value)` tuples are sorted lexicographically by `name`.
- `driver_versions: map<string,string>`
- `determinism_class_map: map<string, enum("E0","E1","NON_COMPARABLE")>`:
  - declares per-field comparator class used by `CompareTrace`.
- Tier binding:
  - `BITWISE`: fixed collective algorithm/chunk order/accumulation dtype-order and `atomic_reductions_allowed=false`.
  - `TOLERANCE`: explicit per-field tolerance bands and E1 comparator profile.

### II.H Divergence Policy (Normative)
- `replay_mode: enum("STRICT_E0","TOLERANT_E1")`.
- `STRICT_E0`: bitwise equality on declared E0 fields.
- `TOLERANT_E1`: explicit per-field tolerance bands only (no implicit tolerances).
- On first divergence: emit `REPLAY_DIVERGENCE`, record deterministic diagnostics, and stop replay.
- Determinism conformance governance:
  - certificate must include `determinism_conformance_suite_id`.
  - verifier rejects certificates with unknown or revoked conformance suite IDs.

### II.I Comparison Profiles (Normative)
- Profile A (`same_world_size_same_rankmap`):
  - Preconditions: identical `world_size`, identical rank mapping.
  - E0 fields include per-rank sample indices and per-rank iterator keys.
- Profile B (`different_world_size`):
  - Preconditions: dataset snapshot and sampler contract identical, but `world_size` differs.
  - Per-rank sample indices are marked `NON_COMPARABLE`.
  - Compare deterministic global fields only: `dataset_snapshot_id`, `sampler_config_hash`, `effective_q`, replay token lineage, and declared aggregate metrics under E1 policy.
- Verifier must record selected comparison profile in replay report and treat mismatched profile selection as deterministic failure.

---

## 3) Initialization

1. Load policy definitions.
2. Load traces/checkpoints.
3. Validate hash integrity.

---

## 4) Operator Manifest

- `Glyphser.Replay.ComputeReplayToken`
- `Glyphser.Replay.VerifyRNGOwnership`
- `Glyphser.Replay.CompareTrace`
- `Glyphser.Replay.VerifyRestore`
- `Glyphser.Error.Emit`

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

**Operator:** `Glyphser.Replay.ComputeReplayToken`  
**Category:** IO  
**Signature:** `(state -> token)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical token derivation by declared formula.  
**Preconditions / Postconditions:** required fields present.  
**Edge cases:** missing optional fields disallowed if formula requires them.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** canonical field order.  
**Complexity note:** O(serialized_state_size).  
**Failure behavior:** deterministic token-computation error.  
**Dependencies:** canonical serializer/hash function.  
**Test vectors:** fixed state -> token snapshots.

**Operator:** `Glyphser.Replay.VerifyRNGOwnership`  
**Category:** IO  
**Signature:** `(trace -> ownership_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** verifies only declared stochastic operators consume RNG offsets.  
**Preconditions / Postconditions:** trace has rng metadata.  
**Edge cases:** zero-draw runs.  
**Numerical considerations:** counter arithmetic in uint64.  
**Ordering/tie handling:** trace order.  
**Complexity note:** O(trace_events).  
**Failure behavior:** `RNG_CONSUMPTION_VIOLATION`.  
**Dependencies:** operator manifest ownership declarations.  
**Test vectors:** valid/invalid ownership traces.

**Operator:** `Glyphser.Replay.CompareTrace`  
**Category:** IO  
**Signature:** `(trace_a, trace_b, comparison_profile -> divergence_summary)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** compares trace fields under declared determinism class rules using `docs/layer2-specs/Trace-Sidecar.md` schema, active determinism profile, and the selected comparison profile from Section II.I:
- E0 fields: exact byte equality (`replay_token`, hashes, `operator_id`, `operator_seq`, state fingerprints, decision/status codes),
- E1 fields: tolerance comparisons as declared by profile/field policy (for example numeric metrics), using
  `|a-b| <= max(abs_tol, rel_tol * max(|a|, |b|))` with deterministic per-field `abs_tol`/`rel_tol`,
  where `abs_tol` and `rel_tol` are sourced from the active determinism profile (or field overrides). If unspecified, defaults are `abs_tol = EPS_EQ` and `rel_tol = 0`.
- key-space and record ordering must match exactly in canonical `(t, rank, operator_seq)` order.
- profile mismatch rule: if `comparison_profile` is missing, unknown, or inconsistent with trace preconditions, return deterministic divergence failure (`REPLAY_DIVERGENCE`) with explicit reason in diagnostics.
**Preconditions / Postconditions:** identical schema keys/types.  
**Edge cases:** different lengths.  
**Numerical considerations:** exact for E0 fields, threshold for E1.  
**Ordering/tie handling:** canonical `(t, rank, operator_seq)` order.  
**Complexity note:** O(trace_size).  
**Failure behavior:** deterministic divergence report; emits `REPLAY_DIVERGENCE` on first mismatch under selected replay mode.  
**Dependencies:** determinism-class map.  
**Test vectors:** replay-equivalent and divergent pairs.

---

**Operator:** `Glyphser.Replay.VerifyRestore`  
**Category:** Replay  
**Signature:** `(checkpoint_blob, restored_state, replay_token -> restore_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Verifies that restore state and replay token exactly match checkpoint commitments and deterministic replay contracts.

## 6) Procedure

```text
1. ComputeReplayToken for both runs
2. VerifyRNGOwnership for both traces
3. CompareTrace(trace_a, trace_b, comparison_profile)
4. VerifyRestore(checkpoint_blob, restored_state, replay_token)
5. Return replay_report
```

---

## 7) Trace & Metrics

### Logging rule
Every replay check emits deterministic divergence records.

### Trace schema
- `run_header`: token formulas, policy hash
- `iter`: check_id, result, divergence_location
- `run_end`: status, divergence_summary

### Metric schema
- `divergence_count`, `first_divergence_t`, `rng_violation_count`

### Comparability guarantee
Comparable iff policy hash, token formulas, and trace schema are identical.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes deterministic ordering, explicit stochastic ownership, trace compliance.

#### VII.B Operator test vectors (mandatory)
Token, RNG ownership, and trace comparison vectors.

#### VII.C Golden traces (mandatory)
Golden replay-equivalent and known-divergence fixtures.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 for replay report identity.

#### VIII.B Allowed refactor categories
- Comparator optimization preserving report semantics.

#### VIII.C Equivalence test procedure (mandatory)
Exact comparison of divergence summary outputs.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- replay policy hash, token formulas, comparator config.

### Serialization
- deterministic CBOR/JSON.

### Restore semantics
- restored contract yields identical replay verdicts.
