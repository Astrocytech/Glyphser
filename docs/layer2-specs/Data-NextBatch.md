# Universal Machine Learning Operating System — Data NextBatch
**EQC Compliance:** This specification follows EquationCode (EQC) v1.1 merged single-file format (Option A): 10 top-level sections, global semantics first, operator-owned math, control-flow-only procedure, deterministic contracts, and replayable stochasticity.

**Algorithm:** `Glyphser.Data.NextBatch`  
**Purpose (1 sentence):** Deliver fully deterministic, memory-efficient, world_size-independent global batch sampling with block-shuffled epoch permutations for training and strict sequential access for evaluation/inference, scalable to 100 B+ sample datasets with O(1) per-sample index resolution after O(num_blocks) preprocessing.  
**Spec Version:** `Glyphser.Data.NextBatch` | 2026-02-18 | Authors: Olejar Damir (with EQC team improvements)  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Deterministic data loading and shuffling for reproducible large-scale distributed ML training and evaluation.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `Glyphser.Data.NextBatch`
- **Purpose (1 sentence):** Memory-efficient deterministic global sampling with epoch-wise seeded shuffling that is independent of world_size and rank.
- **Spec Version:** `Glyphser.Data.NextBatch` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Scalable deterministic data iteration for any dataset cardinality.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Not an optimization operator.
- Primary guarantee: identical global virtual sequence for any (world_size, rank) pair given identical manifest/seed/dataset_cardinality.
- Comparison rule: exact index equality (uint64).

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` derived deterministically.
- PRNG family: `Philox4x32-10`
- Randomness locality: only inside `SeededBlockPermute` and `SeededIntraBlockMap`
- Replay guarantee: fully replayable given `(kernel_replay_token, manifest_hash, dataset_key, epoch, global_position, world_size, rank, sampler_block_size)`
- Replay token contribution: `data_replay_t = SHA-256(CBOR_CANONICAL(["nextbatch", [kernel_replay_token, dataset_key, uint64(epoch), uint64(global_position), uint32(world_size), uint32(rank)]]))`
- Contract-critical hash primitive: `SHA-256(CBOR_CANONICAL(...))`.

### 0.C Numeric Policy
- All indices, cardinalities, positions: uint64 (no wrap-around overflow; explicit bounds checks)
- Block arithmetic: exact integer division/modulo
- No floating-point in core path
- Constants: `DEFAULT_BLOCK_SIZE = 1_048_576` (2^20)
- Overflow/underflow: abort on detected uint64 overflow in cursor or position arithmetic.
- Approx-equality: exact integer equality only (no tolerance path).
- Normalized exponentials / transcendental functions: N/A for this operator class.

### 0.D Ordering and Tie-Break Policy
- Index base: 0-based
- Global batch formation: ascending global virtual position
- Tie break: lowest original index wins (only relevant for boundary handling)

### 0.E Parallel, Concurrency, and Reduction Policy
- Global batch sequence **independent** of `world_size`
- Sharding: contiguous rank-ordered slices of the global virtual sequence (`global_batch_size % world_size == 0` enforced)
- `world_size=1`: full global batch
- No collectives required; pure local computation

### 0.F Environment and Dependency Policy
- Reference runtime: CPU/GPU agnostic (pure index math)
- Dependencies: manifest.datasets[dataset_key] must contain `cardinality: uint64`, `id`, `version`, `hash`
- `manifest.data.sampler_block_size: uint64` (default 1_048_576)
- Determinism level: `BITWISE` for all emitted indices and cursor state.

### 0.G Operator Manifest
- `Glyphser.Data.NextBatch`
- `Glyphser.Data.SeededBlockPermute` (internal helper)
- `Glyphser.Data.SeededIntraBlockMap` (internal helper)
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- Fully-qualified names: `Glyphser.Data.<Name>_v#`

### 0.I Outputs and Metric Schema
- Declared outputs: `(batch_sample_indices: uint64[], cursor_next, sampling_metadata)`
- Minimum metrics: `epoch`, `global_position`, `is_shuffled`, `effective_batch_size`, `blocks_materialized`
- DP/accounting metadata output: `subsampling_mode`, `sampling_mode`, `effective_q`, `sampler_block_size`, `sampler_config_hash`
- Deterministic definitions:
  - `B_eff = global_batch_size`
  - `effective_q = float64(B_eff) / float64(N)`
  - `subsampling_mode = "SHUFFLE_WITHOUT_REPLACEMENT"` in train mode, `"NONE"` in eval/infer mode
  - `sampling_mode = "SHUFFLE_WITHOUT_REPLACEMENT_BLOCK_AFFINE_V1"` in train mode, `"SEQUENTIAL_V1"` in eval/infer mode
  - encoding rule: all mode strings used in hashes are UTF-8 CBOR text strings with no alternate normalization.
  - `sampler_config_hash = SHA-256(CBOR_CANONICAL([sampling_mode, [sampler_block_size, drop_last, "epoch_seed_rule", "intra_block_affine_coprime", "rank_contiguous_shard"]]))`
- Completion status: `success | failed` with deterministic reason codes from 0.K.

### 0.J Spec Lifecycle Governance
- Reproducibility-breaking changes to sequence formation, sharding, or cursor progression require MAJOR version bump.
- Non-breaking performance-only changes (cache/prefetch without sequence changes) require MINOR bump.
- Equivalence target: E0 exact index-sequence equivalence.

### 0.K Failure and Error Semantics
- Global error model: abort-only
- Failure codes: `INVALID_DATASET_KEY`, `CARDINALITY_MISMATCH`, `BATCH_SIZE_INCONSISTENT`, `GLOBAL_POSITION_EXCEEDS_CARDINALITY`, `INVALID_STAGE_TYPE`
- Failure record fields: `t`, `failure_code`, `dataset_key`, `data_replay_t`

### 0.L Input/Data Provenance
- `dataset_cardinality` must match registered immutable dataset hash

### 0.M Recommended Presets
- `train_shuffle`: block-based + train mode
- `eval_sequential`: no-shuffle + ascending indices
- `streaming_infinite`: wrap-around with epoch seed rotation

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
- `data_cursors: map<string, {epoch: uint64, global_index: uint64}>` (per dataset_key)

### I.B Inputs and Hyperparameters
- `dataset_key: string`
- `world_size: uint32`
- `rank: uint32` (0-based)
- `global_batch_size: uint64` (from manifest)
- `stage_type: "train" | "eval" | "infer"`

### I.C Constraints and Feasible Set
- `global_batch_size % world_size == 0`
- `global_batch_size > 0`
- if `world_size > 1`, then `global_batch_size >= world_size`
- `sampler_block_size > 0`
- `dataset_key` exists in manifest.datasets
- Degenerate train/drop-last guard (normative): if `stage_type=="train"` and `drop_last==true` and `global_batch_size > N`, configuration is invalid and MUST abort during validation (zero-batch epochs are forbidden by default policy).
- Train epoch policy (normative): strict bijection without replacement over `[0..N-1]` per epoch; no intra-epoch wrap in train mode.
- If `drop_last=true`, train epoch size is `floor(N/global_batch_size) * global_batch_size`.
- If `drop_last=false`, final train step may be partial; no repeated samples are allowed within the same epoch.
- For `stage_type in {"eval","infer"}`, `drop_last` is ignored; final partial batch MUST be emitted.

### I.D Transient Variables
- `N`, `epoch_seed`, `block_order`, `current_block_perms` (lazy map)

### I.E Invariants and Assertions
- Same `(manifest_hash, epoch, global_position)` → identical sample index
- Eval/infer: sample_indices == [global_pos, global_pos+1, …] % N
- Train: permutation is a bijection over [0 … N-1]
- `NextBatch` is cursor-pure: it consumes `cursor_in` and returns `cursor_next`; persistence is owned by kernel/checkpoint state.
- DP alignment invariant: emitted `subsampling_mode` must match DP accountant assumption for the same run.

---

## 3) Initialization

1. `cursor <- cursor_in` (caller-owned persistent cursor; default `{epoch:0, global_index:0}` at first use)
2. `N <- manifest.datasets[dataset_key].cardinality`
3. If new epoch (`cursor.global_index == 0`): compute `epoch_seed = SHA-256(CBOR_CANONICAL(["nextbatch_epoch_seed", [kernel_replay_token, manifest_hash, dataset_key, uint64(cursor.epoch)]]))[0:16]` (Philox seed)

---

## 4) Operator Manifest

Active operators:
- `Glyphser.Data.NextBatch`
- `Glyphser.Data.SeededBlockPermute`
- `Glyphser.Data.SeededIntraBlockMap`
- `Glyphser.Error.Emit`

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

**Operator:** `Glyphser.Data.NextBatch`  
**Category:** Data  
**Signature:** `(dataset_key, world_size, rank, stage_type, cursor_in -> batch_sample_indices: uint64[], cursor_next, sampling_metadata)`  
**Purity class:** PURE  
**Determinism:** deterministic (RNG only inside helpers for train shuffling)  
**Definition:** Computes the next micro-batch of original sample indices according to global virtual order from explicit caller-provided cursor state. Guarantees identical sequence across any distributed configuration and deterministic cursor transition.
**Preconditions / Postconditions:** dataset exists and cardinality is known; `cursor_next` is advanced exactly once on success and must be persisted by caller.  
**Edge cases:** `N < global_batch_size`, final partial range with `drop_last=true`, `world_size=1`.  
**Numerical considerations:** uint64-only arithmetic; explicit bounds checks before modulo/division.  
**Ordering/tie handling:** ascending global virtual positions; contiguous rank shard order.  
**Complexity note:** O(micro_batch_size) per call + O(num_blocks) epoch permutation materialization.  
**Failure behavior:** emits 0.K error codes and aborts deterministically.  
**Dependencies:** `SeededBlockPermute`, `SeededIntraBlockMap`, manifest data schema.  
**Test vectors:** see VII.B (single-rank, multi-rank, large-N, restore continuity).

**Operator:** `Glyphser.Data.SeededBlockPermute`  
**Category:** Data  
**Signature:** `(num_blocks, epoch_seed -> block_order: uint64[])`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Fisher-Yates shuffle of [0 … num_blocks-1] using Philox seeded by epoch_seed. Materializes only O(num_blocks) memory. For datasets with a short tail block, caller passes only full-size block count and keeps the tail block fixed at the end.
**Preconditions / Postconditions:** `num_blocks > 0`; output is a bijection over block IDs.  
**Edge cases:** `num_blocks = 1`.  
**Numerical considerations:** integer-only index swaps.  
**Ordering/tie handling:** deterministic swap order by ascending iteration index.  
**Complexity note:** O(num_blocks) time and memory.  
**Failure behavior:** abort on invalid `num_blocks` or seed derivation failure.  
**Dependencies:** Philox implementation, deterministic seed derivation.  
**Test vectors:** fixed seed -> exact permutation sequence.

**Operator:** `Glyphser.Data.SeededIntraBlockMap`  
**Category:** Data  
**Signature:** `(block_id, local_pos, block_size, epoch_seed, N -> original_index: uint64)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Computes an explicit affine bijection inside the selected block. Let `block_start = block_id * block_size`, `m = min(block_size, N - block_start)`, and derive `(k0, k1)` from Philox with counter tuple `(epoch_seed, block_id)`. If `m=1`, return `block_start`. Otherwise choose `a` deterministically from seed material:
1. `a <- 1 + (k0 mod (m-1))`
2. for `i in [0..m-2]`: let `cand = 1 + ((a - 1 + i) mod (m-1))`; choose first `cand` with `gcd(cand, m) == 1`
3. if none found (unreachable for `m>1`), abort with deterministic failure code `CONTRACT_VIOLATION`
Then set `c = k1 mod m`, compute `j = (a * local_pos + c) mod m`, and `original_index = block_start + j`.
This is bijective because `gcd(a,m)=1` by construction.
**Preconditions / Postconditions:** `local_pos < m`; output index in `[0, N-1]`; mapping is a permutation over `[block_start, block_start + m - 1]`.  
**Edge cases:** short final block, `N % block_size != 0`.  
**Numerical considerations:** integer modular arithmetic only; no float path; all intermediate arithmetic checked for uint64 overflow before modulo.  
**Ordering/tie handling:** deterministic mapping for every `(block_id, local_pos)`.  
**Complexity note:** O(1) per lookup.  
**Failure behavior:** abort on invalid block bounds.  
**Dependencies:** Philox counter path and epoch seed.  
**Test vectors:** fixed tuple -> exact mapped index; per-block bijection test over all `local_pos in [0, m-1]`.

---

## 6) Procedure

```text
1. cursor = cursor_in
2. N = manifest.datasets[dataset_key].cardinality
3. global_pos = cursor.global_index
4. global_batch_size = manifest.global_batch_size
5. If global_batch_size % world_size != 0: Error.Emit(BATCH_SIZE_INCONSISTENT); abort
5a. If world_size > 1 and global_batch_size < world_size: Error.Emit(BATCH_SIZE_INCONSISTENT); abort
6. micro_batch_size = global_batch_size // world_size
7. rank_start = rank * micro_batch_size
7b. sampler_block_size = manifest.data.sampler_block_size or DEFAULT_BLOCK_SIZE
7c. If sampler_block_size == 0: Error.Emit(BATCH_SIZE_INCONSISTENT); abort

8. if stage_type in {"eval", "infer"}:
       is_shuffled = false
       sampling_mode = "SEQUENTIAL_V1"
       # eval/infer ignore drop_last and always emit terminal partial ranges
       batch_positions = [global_pos + rank_start + i for i in 0..micro_batch_size-1]
       batch_indices = [p % N for p in batch_positions]
   else:
       is_shuffled = true
       sampling_mode = "SHUFFLE_WITHOUT_REPLACEMENT_BLOCK_AFFINE_V1"
       block_size = sampler_block_size
       num_full_blocks = N // block_size
       has_tail = (N % block_size) != 0
       block_order = SeededBlockPermute(num_full_blocks, epoch_seed) if num_full_blocks > 0 else []

       batch_indices = []
       epoch_limit = N
       if manifest.data.drop_last == true:
           num_full_batches = N // global_batch_size
           epoch_limit = (N // global_batch_size) * global_batch_size
       for i in 0..micro_batch_size-1:
           p = global_pos + rank_start + i
           if p >= epoch_limit:  # strict no-wrap train epoch policy
               break
           block_id_global = p // block_size
           if has_tail and block_id_global == num_full_blocks:
               perm_block_id = num_full_blocks  # keep short tail block fixed
           else:
               perm_block_id = block_order[block_id_global]
           local_pos = p % block_size
           orig_idx = SeededIntraBlockMap(perm_block_id, local_pos, block_size, epoch_seed, N)
           batch_indices.append(orig_idx)

9. sampler_config_hash = SHA-256(CBOR_CANONICAL([sampling_mode, [sampler_block_size, manifest.data.drop_last, "epoch_seed_rule", "intra_block_affine_coprime", "rank_contiguous_shard"]]))
10. epoch_limit_for_advance = N
    if stage_type == "train" and manifest.data.drop_last == true:
        epoch_limit_for_advance = (N // global_batch_size) * global_batch_size
11. produced_global_count = global_batch_size
    if stage_type == "train":
        remaining = epoch_limit_for_advance - global_pos
        if remaining <= 0:
            produced_global_count = 0
        else if remaining < global_batch_size:
            produced_global_count = remaining
12. cursor.global_index += produced_global_count
13. if cursor.global_index >= epoch_limit_for_advance:
        cursor.epoch += 1
        cursor.global_index = 0   # start new epoch
14. return batch_indices, cursor, {sampling_mode, sampler_config_hash}
```

**Scalability & Algorithmic Guarantees (v2):**
- Memory: O(num_blocks) worst-case (~1 MiB for 1 B samples with 1 M block_size); lazy per-batch block materialization possible in future.
- Time: O(micro_batch_size) per call with O(1) intra-block mapping.
- Exact bijection in train mode within each epoch; perfect reproducibility across restarts, world_size, hardware.
- Bijection proof sketch: full blocks are permuted bijectively among full blocks; each block uses affine bijection over its local domain; tail block is mapped only to itself with its own domain length, so global mapping is a permutation over `[0, N)`.
- drop_last behavior is configurable via manifest (`drop_last=false` default).
- For `drop_last=false`, terminal train step may be partial and is emitted without replacement.

---

## 7) Trace & Metrics

### Logging rule
Each invocation emits one deterministic trace record with cursor-before/cursor-after and replay token contribution.

### Trace schema (minimum required)
- `run_header`: `dataset_key`, `cardinality`, `sampler_block_size`, `is_shuffled_per_stage`
- `iter`: `t`, `epoch`, `global_position`, `is_shuffled`, `micro_batch_size`, `global_batch_size`, `subsampling_mode`, `sampling_mode`, `sampler_config_hash`, `effective_q`, `epoch_seed_hash`, `data_replay_t`
- `run_end`: final epoch count, total_samples_seen

### Metric schema
- `epoch`, `global_position`, `effective_batch_size`, `blocks_materialized_this_epoch`

### Comparability guarantee
Two runs are comparable iff dataset snapshot/hash, sampler config, replay token definition, and emitted metric schema are identical.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes symbol completeness, deterministic ordering, total state updates (only cursor), explicit RNG locality, edge-case totality.
- Must reject `drop_last==true && global_batch_size > N` for train stage as invalid configuration.

#### VII.B Operator test vectors (mandatory)
- world_size=1, rank=0: full global sequence matches sequential + shuffle
- world_size=8, any rank: contiguous shards reconstruct global sequence exactly
- N=10^9+, block_size=1M: no OOM, identical across runs
- eval mode: always sequential indices
- checkpoint/restore mid-epoch: identical continuation

#### VII.C Golden traces (mandatory)
Golden runs for N=10^6, 10^9 with multiple world_sizes; exact index sequences verified.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0: exact sample index sequences and cursor state
- E1: identical training dynamics (loss curves within noise)

#### VIII.B Allowed refactor categories
- Intra-block mapping optimization (Feistel, AES-based, etc.) preserving bijection
- Prefetch / cache-friendly block loading
- Weighted/class-balanced extensions (with manifest flag and extra seed stream)

#### VIII.C Equivalence test procedure (mandatory)
- 5 seeds × 3 world_sizes × 2 modes
- Compare full batch index sequences (exact match required for E0)

---

## 10) Checkpoint/Restore

### Checkpoint contents
- `data_cursors` map (epoch + global_index per dataset_key only)

### Serialization
- Deterministic CBOR with fixed field order

### Restore semantics
- Identical subsequent batch sequences under same manifest/seed
- Mid-epoch restore supported (no re-shuffle of current epoch)
