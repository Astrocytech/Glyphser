# Universal Machine Learning Operating System — Differential Privacy Gradient Applicator
**EQC Compliance:** This specification follows EquationCode (EQC) v1.1 merged single-file format (Option A): 10 top-level sections, global semantics first, operator-owned math, control-flow-only procedure, deterministic contracts, and replayable stochasticity.

**Algorithm:** `Glyphser.DifferentialPrivacy.Apply`  
**Purpose (1 sentence):** Apply deterministic clipping (with FlashDP-fused and PEFT-aware paths), smart privacy budget allocation, heterogeneous per-layer/per-group noise, pre-computed sigma schedules, scaling-law projections, and PLD-default accounting with safety-reserve abort-on-budget semantics for regulated frontier LLM training.  
**Spec Version:** `Glyphser.DifferentialPrivacy.Apply` | 2026-02-18 | Authors: Olejar Damir (with EQC team improvements)  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** DP-SGD and related private first-order optimization at LLM/frontier scale.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `Glyphser.DifferentialPrivacy.Apply`
- **Purpose (1 sentence):** Differential privacy mechanism for gradients with deterministic clipping, heterogeneous noise scheduling, and exact accounting.
- **Spec Version:** `Glyphser.DifferentialPrivacy.Apply` | 2026-02-18 | Authors: Olejar Damir (with EQC team improvements)
- **Domain / Problem Class:** DP-SGD and related private first-order optimization at LLM/frontier scale.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: `a ≼ b iff a <= b + EPS_EQ` for budget and threshold checks
- `EPS_EQ = 1e-10` in binary64
- Invalid objective policy: any NaN/Inf in gradients, sigma maps, or accountant state is terminal and mapped to deterministic failure code.

### 0.B Reproducibility Contract
- Seed space: `seed in {0..2^64-1}`
- PRNG family: `Philox4x32-10`
- Randomness locality: all sampling occurs only inside `Glyphser.DifferentialPrivacy.GenerateNoise`
- Replay guarantee: replayable given `(seed, PRNG family, numeric policy, ordering policy, parallel policy, environment policy)`
- Replay token contribution: `dp_replay_t = SHA-256(CBOR_CANONICAL(["dp_apply", [kernel_replay_token, uint64(t), dp_accountant_state_hash, allocation_mode, fused_kernel, safety_reserve]]))`
- `noise_seed_per_step: bool` (default `false`); when true, counter derivation is `counter = (uint128(t) << 40) + uint128(param_index_hash)` (128-bit arithmetic, no 64-bit wrap)
  - `param_index_hash` is the lower 40 bits of `U64_BE(SHA-256(CBOR_CANONICAL(["dp_param", param_fqn])))`.

### 0.C Numeric Policy
- Critical arithmetic (norms, clipping scales, means, sigma schedules/maps, accountant state): IEEE-754 binary64
- Deterministic reductions: ascending global parameter index with Kahan summation in binary64
- Heterogeneous maps (`sigma_map`, `clip_norm_map`, `sensitivity_map`, `stddev_map`) are processed in binary64 with deterministic group-local Kahan reductions
- Stable norm computation: max-rescaled L2 path + Kahan accumulation
- Optional `log_space_accounting: true` for very long runs (`steps > 10k`)
- Output cast: `manifest.compute_dtype` only at final return
- Rounding mode: round-to-nearest ties-to-even
- Fast-math: forbidden
- Constants: `EPS_EQ=1e-10`, `EPS_DENOM=1e-12`, `EPS_CLIP=1e-8`
- Sigma clamp: per-entry `sigma in [1e-8, 1e8]`
- NaN/Inf policy: abort per 0.K
- Approx-equality: `a ~= b iff |a-b| <= EPS_EQ`
- Accountant reproducibility: accountant path is bitwise reproducible in binary64 for identical inputs and ordering.
- Normalized exponentials: N/A for core DP pipeline except accountant internals, which must use numerically stable log-domain operations.

### 0.D Ordering and Tie-Break Policy
- Index base: `0-based`
- Stable sort required
- Tie break: lowest index wins
- Iteration/reduction order: ascending global parameter index, then ascending rank

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel chunking: fixed 256-element chunks, deterministic merge order
- `parallelism.type: "dp_only" | "3d" | "fsdp2" | "zero3" | "moe"`
- `world_size=1`: exact `(epsilon, delta)` guarantee
- `world_size>1` with `per_sample`/`per_layer`/`per_group`: exact accounting, deterministic all-gather/all-reduce for required statistics
- `world_size>1` with `ghost` local clipping path: allowed with declared `accounting_adjustment_factor`; guarantee documented as `(epsilon', delta)` where `epsilon' >= epsilon`
- `ghost` path policy: in `regulated` mode, ghost clipping is permitted only when `accounting_adjustment_factor` is derived from a versioned audited bound artifact (`ghost_bound_hash`) and `accounting_adjustment_factor >= 1.0`; otherwise abort with `INVALID_DP_CONFIG`.
- `fsdp2/zero3`: ghost clipping uses unsharded logical views when available; only aggregate statistics are all-reduced
- `moe`: per-expert accounting with routing-aware effective sampling rate
- Hierarchical all-reduce path is allowed when `parallelism.hierarchical=true` (deterministic intra-node then inter-node merge order)
- No async updates or unordered reductions permitted.

### 0.F Environment and Dependency Policy
- Reference runtime class: GPU-enabled, distributed-capable
- Compiler/flags: fast-math disabled
- Dependencies: deterministic Philox implementation + verified accountant implementation (`pld` default; `moments`/`rdp`/`f_dp`/`gdp` fallback)
- Determinism level: `BITWISE` for clipping/sigma/accountant outputs; sampled noise is bitwise-replayable given `(seed, rng offsets, numeric policy, determinism profile)`.

### 0.G Operator Manifest
- `Glyphser.DifferentialPrivacy.PreValidation`
- `Glyphser.DifferentialPrivacy.ConfigResolver`
- `Glyphser.DifferentialPrivacy.SensitivityAnalyzer`
- `Glyphser.DifferentialPrivacy.PrivacyBudgetAllocator`
- `Glyphser.DifferentialPrivacy.Clip`
- `Glyphser.DifferentialPrivacy.ClipPerSample`
- `Glyphser.DifferentialPrivacy.GhostClipPerSample`
- `Glyphser.DifferentialPrivacy.PerLayerClip`
- `Glyphser.DifferentialPrivacy.PerGroupClip`
- `Glyphser.DifferentialPrivacy.PerTensorClip`
- `Glyphser.DifferentialPrivacy.PEFTAwareClipHandler`
- `Glyphser.DifferentialPrivacy.FlashEfficientClip`
- `Glyphser.DifferentialPrivacy.BoundedPrivacyAwareAdaptiveClipNorm`
- `Glyphser.DifferentialPrivacy.PrivacyBudgetScheduler`
- `Glyphser.DifferentialPrivacy.DPScalingLawProjector`
- `Glyphser.DifferentialPrivacy.AmplificationByShuffling`
- `Glyphser.DifferentialPrivacy.GenerateNoise`
- `Glyphser.DifferentialPrivacy.Accountant.Update`
- `Glyphser.DifferentialPrivacy.MomentsAccountant.Update`
- `Glyphser.DifferentialPrivacy.PLDAccountant.Update`
- `Glyphser.DifferentialPrivacy.RDPAccountant.Update`
- `Glyphser.DifferentialPrivacy.FDPAccountant.Update`
- `Glyphser.DifferentialPrivacy.GDPAccountant.Update`
- `Glyphser.Error.Emit`
- `Glyphser.DifferentialPrivacy.Apply`

### 0.H Namespacing and Packaging
- Fully-qualified names: `Glyphser.DifferentialPrivacy.<Name>_v#`
- Sidecar mapping is mandatory (`operator -> module/function`).

### 0.I Outputs and Metric Schema
- Declared outputs: `(noisy_gradients, updated_budget, dp_metrics)`
- Minimum metrics: `clip_fraction`, `noise_scale_sigma`, `cumulative_epsilon`, `privacy_budget_remaining`
- Extended metrics: `norm_p50`, `norm_p95`, `norm_max`, `effective_noise_multiplier`, `effective_heterogeneous_multiplier`, `accountant_type_used`, `pld_epsilon_tight`, `gradient_snr`, `group_clip_fraction`, `effective_accumulation_factor`, `projected_final_epsilon`, `privacy_allocation_mode`, `fairness_clip_ratio`, `scaling_law_confidence`, `peft_noise_reduction_factor`
- Completion status: `success | failed` with deterministic reason codes from 0.K.

### 0.J Spec Lifecycle Governance
- Any accountant algorithm change or clipping strategy semantics change requires MAJOR version bump.
- Scheduler mode additions require MINOR bump if backward-compatible.
- Equivalence targets: E0 for clipping/accounting path; E2 for stochastic outputs.

### 0.K Failure and Error Semantics
- Global error model: abort-only with deterministic final record
- Failure codes: `PRIVACY_BUDGET_EXCEEDED`, `INVALID_GRADIENT`, `NAN_IN_SIGMA`, `ACCOUNTANT_OVERFLOW`, `ACCOUNTANT_DIVERGENCE`, `RNG_CONSUMPTION_VIOLATION`, `INVALID_DP_CONFIG`
- `safety_budget_reserve` is a fractional reserve `r in [0,1)`.
- Soft safety warning threshold: `warn_threshold = target_epsilon * (1 - r)`
- Failure record fields: `t`, `failure_code`, `failure_operator`, `dp_replay_t`, `state_fp_t`

### 0.L Input/Data Provenance
- Input gradients originate from kernel-validated model backward pass.
- `sampling_rate`, `batch_size`, effective dataset cardinality, accumulation factor, and routing stats (`moe`) must be traceable to manifest + dataset registry.

### 0.M Recommended Presets
- `llm_flash`: `flash_efficient + per_layer + pld + bounded_adaptive + scaling_law + fsdp2 + fused`
- `peft_max_utility`: `peft_targeted + ghost + pld + budget_allocator + low_noise`
- `regulated_fair`: `bounded_adaptive + per_group + pld + uniform_allocation + safety_reserve=0.12`
- `frontier_trillion`: `hybrid + flash_efficient + pld + dynamic_projection + 3d_parallel`

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
- `cumulative_epsilon_t in R_{>=0}` (binary64)
- `rng_dp_state_t` with deterministic offset ownership
- `clip_norm_state_t` (for adaptive clipping)
- `norm_history_state` (adaptive clipping): fixed-size circular buffer of recent gradient norms plus deterministic write index and count.
- `accountant_state_t` (PLD/moments/RDP/f-DP/gDP internal deterministic state)
- `accumulation_state_t` (partial clipped sums and accumulation counter)

### I.B Inputs and Hyperparameters
- `gradients`
- `security.differential_privacy`:
  - `enabled: bool`
  - `mechanism: "gaussian"`
  - `accountant: "pld" | "moments" | "rdp" | "f_dp" | "gdp"` (default/recommended: `pld`)
  - `subsampling: "SHUFFLE_WITHOUT_REPLACEMENT" | "NONE"`
  - `sampling_mode: string` (from `docs/layer2-specs/Data-NextBatch.md` sampler metadata)
  - `accountant_granularity: "PER_STEP"` (required)
  - `clipping.strategy: "per_sample" | "ghost" | "per_layer" | "per_group" | "per_tensor" | "hybrid" | "peft_targeted" | "adaptive"`
  - `clipping.norm: float | "adaptive"`
  - `clip_norm_map: dict | null`
    - completeness rule: when resolved for a step, `clip_norm_map` MUST contain an entry for every active privacy group `g`.
  - `sensitivity_map: dict | null`
  - `sigma_map: dict | null` (dimensionless multipliers `sigma_g`)
  - `noise.per_layer_multiplier: dict | null`
  - `noise.compression: "none" | "topk_dp" | "sparse_dp"`
  - `fused_kernel: bool` (default `true` for llm presets)
  - `max_microbatch: int` (default `256`)
  - `adaptive_clip_window: uint64` (default `100`, used when `clipping.strategy=="adaptive"`)
  - `noise_multiplier: float` (default `1.0`)
  - `target_epsilon: float`
  - `target_delta: float` (default `1e-5`)
  - `pld_discretization_bins: uint64` (default `1000000`)
  - `pld_truncation_bound: float64` (default `1e-12`)
  - `target_steps: int?`
  - `mode: "fixed" | "budget_adaptive" | "meet_exactly_at_target_steps" | "step_decay" | "dynamic_projection"`
  - `gradient_accumulation_steps: int` (default `1`)
  - `model_scale: float64` (optional; projector hint input)
  - `accumulation_context: {current_step: int, is_final: bool}`
  - `privacy.adaptive_accounting: "conservative" | "heuristic"`
  - `privacy_allocation: "uniform" | "layer_wise" | "custom"`
  - `safety_budget_reserve: float` (default `0.08`)
  - `accounting_adjustment_factor: float` (default `1.0`)
  - `parallelism.hierarchical: bool` (default `false`)
  - `parallelism.type: "dp_only" | "3d" | "fsdp2" | "zero3" | "moe"`
  - `training_phase: "warmup" | "main" | "cooldown"`
  - `public_modules: list | null` (zero privacy-cost modules)
- `sampling_rate`, `effective_batch_size`, `model_scale`, `t`
  - `accountant_hint` (derived) = configured `accountant` enum value for projector/scheduler hinting.

### I.C Constraints and Feasible Set
- Unconstrained optimization context.
- Runtime constraints: `target_epsilon >= 0`, `target_delta in (0,1)`, `noise_multiplier >= 0` (debug mode permits `0`), valid clipping strategy/scheduler/accountant, deterministic contract checks.
- PLD constraints: when `accountant=="pld"`, `pld_discretization_bins` and `pld_truncation_bound` are mandatory-effective (explicit or defaults), and MUST be included in DP config hash commitment.
- DP config hash commitment rule: all configured DP fields that influence behavior (including optional `adaptive_clip_window` and `model_scale` when present) MUST be included in the canonical DP config hash (`dp_policy_hash` input).

### I.D Transient Variables
- `clipped_gradients`, `per_sample_norms`, `per_group_norms`, `sigma_map_t`, `stddev_map_t`, `noise_t`, `averaged_gradients`, `projected_epsilon`, `allocation_map`, `amplification_factor`

### I.E Invariants and Assertions
- `cumulative_epsilon` is finite and non-decreasing
- output tensor shape equals input gradient shape
- all critical reductions follow fixed deterministic ordering
- clipping may occur per micro-batch; accountant update and noise draw occur once per optimizer step.

### II.F Mechanism Definition (Formal)
- Adjacency: record-level adjacency (datasets differ by one record via add/remove or replace).
- Parameter space is partitioned into disjoint groups `g in G` by `privacy_allocation`.
- Per-group sensitivity bound: for each sample `i`, clipped gradient satisfies `||clip_g(grad_{i,g})||_2 <= C_g`.
- Per-optimizer-step release for group `g`:
  `G_tilde_g = (1/B_eff) * (sum_i clip_g(grad_{i,g}) + N(0, (sigma_g * C_g / B_eff)^2 I))`,
  where `B_eff` is the effective optimizer-step batch size after accumulation.
- `sigma_map_t[g]` is the dimensionless multiplier `sigma_g`.
- `stddev_map_t[g]` is derived deterministically as `stddev_map_t[g] = sigma_map_t[g] * C_g / B_eff`.
- Group composition at a step uses the selected accountant (`PLD` default, `RDP`/`moments`/`f_dp`/`gdp` fallback) with explicit `sampling_rate`, `subsampling`, and optional `amplification_factor`.
- Normative heterogeneous composition rule:
  - Renyi-order grid is config-bound and deterministic (`alpha_grid` in DP config); default:
    - `alpha_grid = [1.25, 1.5, 1.75, 2, 2.5, 3, 4, 5, 6, 8, 10, 12, 16, 24, 32, 48, 64]`.
  - For each Renyi order `alpha` in `alpha_grid`, compute `RDP_step(alpha) = sum_g RDP_g(alpha; q, sigma_g)` using a uniform global sampling rate `q = effective_batch_size / dataset_cardinality` for all groups.
  - Compose across optimizer steps by summation in deterministic step order.
  - Convert to `(epsilon, delta)` via deterministic minimization over the fixed `alpha` grid.
  - PLD path is allowed as primary implementation only when `pld_discretization_bins`, `pld_truncation_bound`, and declared error bound are config-bound and included in trace.
- Step composition: accountant composes optimizer steps in deterministic order; `(epsilon, delta)` reported from accountant conversion per optimizer step.
- Ghost clipping: when enabled, accountant input uses `sampling_rate' = min(1.0, accounting_adjustment_factor * sampling_rate)` and requires audited bound artifact in regulated mode.
- zero-sensitivity rule: groups with sensitivity `0` MUST set `sigma_g=0`, `stddev_g=0`, and contribute zero privacy cost in accountant updates.

### II.G Subsampling/Accounting Alignment (Normative)
- `subsampling` must be one of `SHUFFLE_WITHOUT_REPLACEMENT` or `NONE`.
- Normative mapping:
  - sampler `SHUFFLE_WITHOUT_REPLACEMENT` -> accountant uses fixed-size without-replacement composition.
  - sampler `NONE` -> accountant uses full-batch composition (`q=1`).
- Accountant assumptions must match sampler behavior declared in `docs/layer2-specs/Data-NextBatch.md`.
- Heterogeneous-group rule: group-specific subsampling rates are not supported in this version; composition uses the single global sampling rate `q` for all groups.
- If exact match is unavailable, run must declare deterministic approximation policy and log `accounting_approximation_policy` in trace.

### II.H Adaptation Safety (Normative)
- Any adaptation of `clip_norm`, `allocation_map`, or budget schedule that depends on private gradients must use:
  - DP-sanitized aggregates only, or
  - explicitly budgeted adaptation composed into the same accountant state.
- Adaptation budget consumption (`delta_eps`) must be logged and included in replay/checkpoint accountant state.

### II.I DP Metric Definitions (Normative)
- `gradient_snr = mean(abs(averaged_clipped)) / (std(noise_step) + EPS_DENOM)`.
- `fairness_clip_ratio = clipped_group_count / max(1, total_group_count)`.
- `scaling_law_confidence` is the confidence output from `DPScalingLawProjector` in `[0,1]`.
- `peft_noise_reduction_factor = sigma_full_model / max(EPS_DENOM, sigma_peft_target)`.
- `effective_heterogeneous_multiplier = sigma_effective / max(EPS_DENOM, sigma_base)`.

---

## 3) Initialization

1. `t <- kernel_t`
2. bind `rng_dp_state <- kernel_master_rng` with DP-owned offset stream
3. load or initialize `cumulative_epsilon <- checkpoint_or_zero`
4. `resolved_cfg <- Glyphser.DifferentialPrivacy.ConfigResolver(dp_config)`
5. initialize accountant state for selected `accountant`
6. precompute sigma schedule/cache for target-based modes using deterministic global inversion (binary search cap `30` iterations; cached for reuse)

---

## 4) Operator Manifest

Active operators (exact wiring table):
- `Glyphser.DifferentialPrivacy.PreValidation`
- `Glyphser.DifferentialPrivacy.ConfigResolver`
- `Glyphser.DifferentialPrivacy.SensitivityAnalyzer`
- `Glyphser.DifferentialPrivacy.PrivacyBudgetAllocator`
- `Glyphser.DifferentialPrivacy.Clip`
- `Glyphser.DifferentialPrivacy.ClipPerSample`
- `Glyphser.DifferentialPrivacy.GhostClipPerSample`
- `Glyphser.DifferentialPrivacy.PerLayerClip`
- `Glyphser.DifferentialPrivacy.PerGroupClip`
- `Glyphser.DifferentialPrivacy.PerTensorClip`
- `Glyphser.DifferentialPrivacy.PEFTAwareClipHandler`
- `Glyphser.DifferentialPrivacy.FlashEfficientClip`
- `Glyphser.DifferentialPrivacy.BoundedPrivacyAwareAdaptiveClipNorm`
- `Glyphser.DifferentialPrivacy.PrivacyBudgetScheduler`
- `Glyphser.DifferentialPrivacy.DPScalingLawProjector`
- `Glyphser.DifferentialPrivacy.AmplificationByShuffling`
- `Glyphser.DifferentialPrivacy.GenerateNoise`
- `Glyphser.DifferentialPrivacy.Accountant.Update`
- `Glyphser.DifferentialPrivacy.MomentsAccountant.Update`
- `Glyphser.DifferentialPrivacy.PLDAccountant.Update`
- `Glyphser.DifferentialPrivacy.RDPAccountant.Update`
- `Glyphser.DifferentialPrivacy.FDPAccountant.Update`
- `Glyphser.DifferentialPrivacy.GDPAccountant.Update`
- `Glyphser.Error.Emit`
- `Glyphser.DifferentialPrivacy.Apply`

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator below explicitly declares `Operator/Category/Signature/Purity class/Determinism/Definition`; the following fields apply to all operators unless overridden inline:
- Preconditions / Postconditions: all typed inputs validated by `PreValidation`; outputs are schema-valid and deterministic under declared policies.
- Edge cases: empty/degenerate tensors, tiny batches, extreme scheduler/accountant boundaries.
- Numerical considerations: binary64 critical math, deterministic ordering, no fast-math.
- Ordering/tie handling: deterministic traversal (index/layer/group order) and stable tie-breaks.
- Complexity note: linear in touched tensor elements unless explicitly noted.
- Failure behavior: abort-only under 0.K with deterministic failure records.
- Dependencies: limited to signature inputs + declared operators in section 4.
- Test vectors: covered by VII.B deterministic and stochastic replay tests.

**Operator:** `Glyphser.DifferentialPrivacy.Apply`  
**Category:** Security  
**Signature:** `(gradients, dp_config, t -> noisy_gradients, updated_budget, dp_metrics)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic control path; stochastic only via `GenerateNoise`  
**Definition:** orchestrates validation, config resolution, sensitivity analysis, allocation, clipping, scheduling, projection guard, noise generation, accounting, and cast. `gradients` input is the deterministic per-optimizer-step micro-batch gradient sequence (not a pre-aggregated full-batch gradient tensor).  
**Failure behavior:** abort with 0.K codes.

**Operator:** `Glyphser.DifferentialPrivacy.PreValidation`  
**Category:** Security  
**Signature:** `(dp_config, t -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates DP hyperparameters, mode/accountant compatibility, finite values, and accumulation context.  
**Failure behavior:** `INVALID_DP_CONFIG`.

**Operator:** `Glyphser.DifferentialPrivacy.ConfigResolver`  
**Category:** Security  
**Signature:** `(dp_config, accumulation_context -> resolved_config)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical deterministic merge of defaults, per-module/group overrides, phase overrides, and accumulation context.

**Operator:** `Glyphser.DifferentialPrivacy.SensitivityAnalyzer`  
**Category:** Security  
**Signature:** `(model_layout, norm_history, routing_stats? -> sensitivity_map)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** estimates deterministic per-layer/group/tensor sensitivity for allocation and heterogenous scheduling.

**Operator:** `Glyphser.DifferentialPrivacy.PrivacyBudgetAllocator`  
**Category:** Security  
**Signature:** `(resolved_cfg, sensitivity_map, norm_history -> allocation_map, clip_norm_map)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** allocates privacy budget by selected policy (`uniform`, `layer_wise`, `custom`) and emits deterministic maps.

**Operator:** `Glyphser.DifferentialPrivacy.Clip`  
**Category:** Security  
**Signature:** `(gradients, clipping_cfg, max_microbatch -> clipped, norms, clip_stats)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** dispatches clipping strategy (`per_sample`, `ghost`, `per_layer`, `per_group`, `per_tensor`, `hybrid`, `peft_targeted`, `adaptive`) with deterministic microbatching.

**Operator:** `Glyphser.DifferentialPrivacy.FlashEfficientClip`  
**Category:** Security  
**Signature:** `(gradients, clip_norm_map, fused_cfg -> clipped_or_averaged, norms, stats)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** fused memory-efficient clip-and-average path for structured large-model parameter layouts. `fused_cfg` is deterministically derived from `resolved_cfg` (`fused_kernel` settings and clipping mode compatibility). Noise generation is not performed here and remains exclusively in `GenerateNoise`.

**Operator:** `Glyphser.DifferentialPrivacy.PEFTAwareClipHandler`  
**Category:** Security  
**Signature:** `(gradients, trainable_mask, public_modules -> clipped, peft_stats)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** applies clipping/noise accounting only to trainable/private adapters and excludes public modules.

**Operator:** `Glyphser.DifferentialPrivacy.BoundedPrivacyAwareAdaptiveClipNorm`  
**Category:** Security  
**Signature:** `(norm_history_state, norms_t, adaptive_accounting_mode -> clip_norm_t, norm_history_state', delta_epsilon_cost)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** bounded adaptive clip norm with deterministic update:
  - let `hist = append(norm_history_state, norms_t)` and keep the last `W` values (fixed window `W` from config),
  - `m = median(hist)` (stable sort; even-cardinality median is average of two middle values),
  - `mad = median(|hist_i - m|)`,
  - `clip_norm_t = max(lower_bound, m + k_mad * mad)` with fixed config constants `lower_bound` and `k_mad`,
  - `delta_eps = 0.01` per adaptive update (or `0` when strategy is non-adaptive),
  - return updated history state and `delta_eps` for accountant composition.

**Operator:** `Glyphser.DifferentialPrivacy.PrivacyBudgetScheduler`  
**Category:** Security  
**Signature:** `(t, cumulative_epsilon, resolved_cfg, allocation_map, training_phase, effective_batch_size -> sigma_map_t)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** returns heterogeneous `sigma_map_t` using precomputed schedules for target-based modes and deterministic runtime refinement for `step_decay`/`dynamic_projection`.

**Operator:** `Glyphser.DifferentialPrivacy.DPScalingLawProjector`  
**Category:** Security  
**Signature:** `(sigma_map_t, remaining_steps, model_scale, accountant_hint -> projected_epsilon, confidence)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** projects long-horizon privacy trajectory for proactive safety control (heuristic only). It does not replace formal accounting; compliance and abort decisions are based only on `Accountant.Update`.

**Operator:** `Glyphser.DifferentialPrivacy.AmplificationByShuffling`  
**Category:** Security  
**Signature:** `(sampling_metadata -> amplification_factor)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes deterministic amplification adjustment for `subsampling="SHUFFLE_WITHOUT_REPLACEMENT"` using policy-bound audited constants:
  - `sampling_metadata` canonical schema (normative): `{effective_q: float64, local_epsilon_hint: float64}` encoded as canonical CBOR map.
  - Let `q = sampling_metadata.effective_q` and `eps_local = sampling_metadata.local_epsilon_hint` (both deterministic inputs for this step).
  - Deterministic bound formula (normative default when both values are present):
    - `eps_shuf_bound = log(1 + q*q*(exp(eps_local) - 1))`
    - `amplification_factor = min(1.0, eps_shuf_bound / max(eps_local, 1e-18))`
  - Conservative fallback:
    - if required inputs are absent, non-finite, or out of range, set `amplification_factor = 1.0` (no amplification credit).
  - Policy override:
    - if an audited policy artifact declares a stricter fixed factor `f`, use `min(amplification_factor, f)` deterministically.

**Operator:** `Glyphser.DifferentialPrivacy.GenerateNoise`  
**Category:** Security  
**Signature:** `(shape, stddev_map_t, rng_dp_state, compression_cfg? -> noise, rng_dp_state')`  
**Purity class:** STATEFUL  
**Determinism:** stochastic (bitwise-replayable sample stream under replay contract with fixed seed/offset/profile)  
**Definition:** isotropic/heterogeneous Gaussian generation with exact RNG offset accounting; consumes per-group standard deviations from `stddev_map_t`; applies variance-aware compression adjustments if configured.

**Operator:** `Glyphser.DifferentialPrivacy.Accountant.Update`  
**Category:** Security  
**Signature:** `(accountant_type, state, sigma_map, sampling_rate, t, delta, subsampling, amplification?, delta_eps? -> epsilon_t, state')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** dispatcher for heterogeneous composition in PLD default path and fallback accountants; forwards `subsampling` and optional `amplification_factor`/`delta_eps` to the selected accountant and composes deterministically.

---

**Operator:** `Glyphser.DifferentialPrivacy.ClipPerSample`  
**Category:** DifferentialPrivacy  
**Signature:** `(per_sample_grads, clip_norm -> clipped_grads, norms)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Deterministically clips each sample gradient to the declared norm bound.

**Operator:** `Glyphser.DifferentialPrivacy.GhostClipPerSample`  
**Category:** DifferentialPrivacy  
**Signature:** `(model, batch, clip_norm -> clipped_grads, norms)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** Computes per-sample clipping via ghost-norm path without full per-sample materialization.

**Operator:** `Glyphser.DifferentialPrivacy.PerLayerClip`  
**Category:** DifferentialPrivacy  
**Signature:** `(gradients, per_layer_norms -> clipped_gradients, layer_stats)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Applies deterministic clipping independently per parameter layer/tensor group.

**Operator:** `Glyphser.DifferentialPrivacy.PerGroupClip`  
**Category:** DifferentialPrivacy  
**Signature:** `(gradients, per_group_norms, group_map -> clipped_gradients, group_stats)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Clips gradients by configured logical groups in stable registration order.

**Operator:** `Glyphser.DifferentialPrivacy.PerTensorClip`  
**Category:** DifferentialPrivacy  
**Signature:** `(gradients, clip_norm_map -> clipped_gradients, tensor_stats)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Clips each trainable tensor with its own deterministic bound.

**Operator:** `Glyphser.DifferentialPrivacy.MomentsAccountant.Update`  
**Category:** DifferentialPrivacy  
**Signature:** `(state, sigma_map, sampling_rate, t, delta, subsampling, amplification_factor?, delta_eps? -> epsilon_t, state_next)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Updates privacy budget using moments accountant composition with explicit subsampling mode and optional amplification/adjustment terms.

**Operator:** `Glyphser.DifferentialPrivacy.PLDAccountant.Update`  
**Category:** DifferentialPrivacy  
**Signature:** `(state, sigma_map, sampling_rate, t, delta, subsampling, amplification_factor?, delta_eps? -> epsilon_t, state_next)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Updates privacy budget using privacy-loss distribution composition (recommended), applying declared subsampling and optional amplification factor deterministically.

**Operator:** `Glyphser.DifferentialPrivacy.RDPAccountant.Update`  
**Category:** DifferentialPrivacy  
**Signature:** `(state, sigma_map, sampling_rate, t, delta, subsampling, amplification_factor?, delta_eps? -> epsilon_t, state_next)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Updates privacy budget via Renyi-DP composition with deterministic order set, using declared subsampling mode and optional amplification factor.

**Operator:** `Glyphser.DifferentialPrivacy.FDPAccountant.Update`  
**Category:** DifferentialPrivacy  
**Signature:** `(state, sigma_map, sampling_rate, t, delta, subsampling, amplification_factor?, delta_eps? -> epsilon_t, state_next)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Updates privacy budget via f-DP conversion path for configured compatibility mode.

**Operator:** `Glyphser.DifferentialPrivacy.GDPAccountant.Update`  
**Category:** DifferentialPrivacy  
**Signature:** `(state, sigma_map, sampling_rate, t, delta, subsampling, amplification_factor?, delta_eps? -> epsilon_t, state_next)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Updates privacy budget via Gaussian-DP approximation path for configured compatibility mode.

## 6) Procedure

```text
1. PreValidation(dp_config, t) -> abort on invalid.
1b. Sampling/accountant compatibility check (single deterministic gate):
    - valid iff:
      - (`sampling_mode in {"SHUFFLE_WITHOUT_REPLACEMENT_BLOCK_AFFINE_V1"}` and `subsampling == SHUFFLE_WITHOUT_REPLACEMENT`) OR
      - (`sampling_mode == "SEQUENTIAL_V1"` and `subsampling == NONE`)
    - otherwise emit `INVALID_DP_CONFIG` and abort.
2. resolved_cfg <- ConfigResolver(dp_config, accumulation_context)
2b. sensitivity_map <- SensitivityAnalyzer(...) when allocation/adaptive mode enabled.
3. allocation_map, clip_norm_map <- PrivacyBudgetAllocator(resolved_cfg, sensitivity_map, norm_history)
4. If clipping.strategy == "adaptive":
   (clip_norm_t, clip_norm_state', delta_eps) <- BoundedPrivacyAwareAdaptiveClipNorm(...)
   else delta_eps <- 0.
5. Let `micro_seq` be the deterministic ordered micro-batch sequence for the current optimizer step.
6. Initialize deterministic accumulation buffer for clipped micro-gradients.
7. For each `micro_idx, micro_gradients` in `micro_seq`:
   7a. If fused_kernel == true and per-layer compatible:
          (clipped_micro, norms, clip_stats) <- FlashEfficientClip(micro_gradients, clip_norm_map, fused_cfg)
       else
          (clipped_micro, norms, clip_stats) <- Clip(micro_gradients, resolved_cfg, max_microbatch)
   7b. Accumulate clipped_micro in deterministic order.
8. averaged_clipped <- deterministic_average(accumulated_clipped_micro, gradient_accumulation_steps)
8b. effective_batch_size <- global_batch_size * gradient_accumulation_steps
8c. dataset_cardinality <- sampler_metadata.dataset_cardinality
9. sigma_map <- PrivacyBudgetScheduler(t, cumulative_epsilon, resolved_cfg, allocation_map, training_phase, effective_batch_size)
9b. stddev_map[g] <- sigma_map[g] * clip_norm_map[g] / effective_batch_size   # for each group g
9c. sampling_rate <- effective_batch_size / dataset_cardinality
10. remaining_steps <- (target_steps is defined) ? max(0, target_steps - t) : 0
10a. model_scale_arg <- (resolved_cfg.model_scale is defined) ? resolved_cfg.model_scale : null
10b. projected_epsilon, scaling_conf <- DPScalingLawProjector(sigma_map, remaining_steps, model_scale_arg, accountant)  # pass configured accountant string as accountant_hint
11. If projected_epsilon > target_epsilon: Error.Emit(PRIVACY_BUDGET_EXCEEDED, ...); abort.
12. If subsampling == "SHUFFLE_WITHOUT_REPLACEMENT":
      sampling_metadata <- {effective_q: sampling_rate, local_epsilon_hint: cumulative_epsilon}
      amplification_factor <- AmplificationByShuffling(sampling_metadata)
13. (noise_step, rng_dp_state') <- GenerateNoise(shape(averaged_clipped), stddev_map, rng_dp_state, noise.compression)
14. noisy_binary64 <- averaged_clipped + noise_step
15. (cumulative_epsilon, accountant_state') <- Accountant.Update(accountant, accountant_state, sigma_map, sampling_rate, t, target_delta, subsampling, amplification_factor, delta_eps)
16. If cumulative_epsilon > target_epsilon + EPS_EQ: Error.Emit(PRIVACY_BUDGET_EXCEEDED, ...); abort.
17. noisy_gradients <- cast(noisy_binary64, manifest.compute_dtype)
18. Accountant step semantics:
    - `accountant_granularity == PER_STEP`; `t` advances by 1 per optimizer step.
19. emit dp_metrics (`gradient_snr`, `fairness_clip_ratio`, `scaling_law_confidence`, `peft_noise_reduction_factor`, `effective_heterogeneous_multiplier`) and return.
```

---

## 7) Trace & Metrics

### Logging rule
Each DP step emits deterministic trace fields from section 7, including replay token contribution and budget transition.

### Trace schema (minimum required)
- `run_header`: `dp_mode`, `accountant`, `clipping_strategy`, `subsampling`, `sampling_mode`, `sampler_config_hash`, `parallelism.type`, `noise_seed_per_step`, `privacy_allocation_mode`, `fused_kernel`, `safety_budget_reserve`
- `iter`: `t`, `clip_fraction`, `group_clip_fraction`, `noise_scale_sigma`, `effective_noise_multiplier`, `effective_heterogeneous_multiplier`, `effective_accumulation_factor`, `cumulative_epsilon_before`, `cumulative_epsilon_after`, `projected_final_epsilon`, `norm_p50`, `norm_p95`, `norm_max`, `gradient_snr`, `fairness_clip_ratio`, `scaling_law_confidence`, `peft_noise_reduction_factor`, `accountant_type_used`, `pld_epsilon_tight` (if available), `dp_replay_t`
- `run_end`: final epsilon, budget status, accountant summary hash

### Metric schema
- `clip_fraction`, `group_clip_fraction`
- `noise_scale_sigma`, `effective_noise_multiplier`, `effective_heterogeneous_multiplier`
- `effective_accumulation_factor`
- `cumulative_epsilon`, `privacy_budget_remaining`, `projected_final_epsilon`
- Projection semantics: `projected_final_epsilon` is advisory only; authoritative privacy budget is accountant-computed `cumulative_epsilon`.
- `norm_p50`, `norm_p95`, `norm_max`
- `gradient_snr`, `fairness_clip_ratio`, `scaling_law_confidence`, `peft_noise_reduction_factor`
- `accountant_type_used`, `pld_epsilon_tight`
- `privacy_allocation_mode`

### Comparability guarantee
- E0 comparability requires identical clipping/accounting/scheduler traces and replay tokens.
- E2 comparability applies to final noisy gradients under identical stochastic contracts.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes all mandatory lint rules: symbol completeness, no hidden globals, total state updates, explicit stochasticity, deterministic ordering, trace compliance, typed outputs, and deterministic failure semantics.

#### VII.B Operator test vectors (mandatory)
- Deterministic path: DP disabled returns identity gradients and unchanged budget.
- Deterministic path: fixed synthetic gradients verify clipping scales, per-group/per-tensor allocations, and accountant increments in binary64.
- Accumulation path: clipping is per-micro-batch; budget update and noise RNG consumption occur once per optimizer step.
- Heterogeneous path: sigma-map composition matches reference PLD composition.
- Stochastic path: fixed seed reproduces identical RNG offsets, replay tokens, and accountant trajectory.

#### VII.C Golden traces (mandatory)
- Golden runs for `pld`, `moments`, `rdp` (and fallback accountants where configured).
- Golden scenarios for per-group/per-tensor clipping, accumulation, fused kernel, dynamic scheduler, PEFT-targeted clipping, and scaling-law projection.
- PLD must be no looser than moments under matched settings.
- Safety-reserve warning and budget exhaustion must trigger deterministic records.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0: exact clipping scales, sigma-map schedule, accountant outputs, and trace fields
- E1: metric-equivalent privacy/utility curve within declared tolerances
- E2: distribution-equivalent stochastic gradients under same RNG policy

Required for changes:
- accountant/clipping/scheduler/allocation semantics: E0 on deterministic path
- noise sampler internal optimization/compression: E2 minimum

#### VIII.B Allowed refactor categories
- accountant numeric stabilization
- clip kernel vectorization/fusion preserving ordering
- scheduler optimization preserving mode semantics
- operator replacement via version bump + manifest update

#### VIII.C Equivalence test procedure (mandatory)
- 10 seeds per scenario
- Compare epsilon trajectory, sigma-map trajectory, clip/allocation stats, projected epsilon, and noisy distribution diagnostics (KS test, alpha=0.01)
- Verify failure-path equivalence for budget overflow and accountant divergence

---

## 10) Checkpoint/Restore

### Checkpoint contents
- `cumulative_epsilon_t`
- `accountant_state_t`
- `dp_accountant_state_hash = SHA-256(CBOR_CANONICAL(accountant_state_t))` (normative cross-contract identifier)
- accountant internals: PLD/RDP support grid or order set, accumulated privacy state tables/log-MGFs, conversion cache
- `rng_dp_state_t` / offset
- `clip_norm_state_t` (if adaptive)
- `accumulation_state_t`
- `allocation_map_snapshot`, `sigma_schedule_cache`
- `sampling_rate_history_hash_chain`, `sigma_map_history_hash_chain`, `t_micro_counter`
- `per_module_snapshot` (resolved module/group allocation snapshot)
- DP config snapshot (`accountant`, `clipping`, `mode`, `noise_multiplier`, `safety_budget_reserve`, targets)

### Serialization
- deterministic canonical CBOR with fixed field order

### Restore semantics
- Restore under same manifest + seed yields identical post-restore deterministic path (E0 for clipping/accounting).
- Noise outputs remain E2-equivalent under identical RNG replay contract.
