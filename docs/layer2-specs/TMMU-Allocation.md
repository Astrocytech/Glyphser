# Universal Machine Learning Operating System — TMMU Allocation
**EQC Compliance:** This specification follows EquationCode (EQC) v1.1 merged single-file format (Option A): 10 top-level sections, global semantics first, operator-owned math, control-flow-only procedure, deterministic contracts, and replayable stochasticity.

**Algorithm:** `Glyphser.TMMU.PrepareMemory`  
**Purpose (1 sentence):** Perform static liveness analysis, slot-optimal interval-graph coloring, multi-arena size-aware logical slot assignment, and deterministic injective arena-offset logical-address mapping for any UML_Model_IR DAG, guaranteeing bit-identical layout plans, alignment safety, and replayability across large models.  
**Spec Version:** `Glyphser.TMMU.PrepareMemory` | 2026-02-17 | Authors: Olejar Damir (with EQC team improvements)  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Deterministic, size-aware, multi-arena tensor memory planning via interval-graph register allocation for deep learning computation graphs.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `Glyphser.TMMU.PrepareMemory`
- **Purpose (1 sentence):** Statically compute optimal reusable logical slots and deterministic logical addresses with maximal liveness-based reuse.
- **Spec Version:** `Glyphser.TMMU.PrepareMemory` | 2026-02-17 | Authors: Olejar Damir (with EQC team)
- **Domain / Problem Class:** Scalable, reproducible, alignment-aware tensor memory planning for ML graphs.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Not an optimization operator (enables extreme efficiency).
- Primary guarantee: identical logical slots, logical addresses, and tensor_map for identical `(ir_dag, execution_order, mode, replay_token)`.
- Optimization scope clarification:
  - slot count is optimal for interval overlap constraints,
  - total byte footprint across arenas is heuristic (deterministic, not globally optimal).
- Comparison rule: exact equality of logical addresses and live ranges.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` inherited from kernel replay context.
- PRNG family: Philox4x32-10 (not sampled in allocator core path).
- Assignment is 100% deterministic given replay_token.
- Two-level mapping:
  - Logical slot ID (0-based, assigned by optimal greedy linear scan on interval graph).
  - Logical address is deterministic arena offset mapping: for each arena, slots are ordered deterministically and assigned by aligned prefix-sum offsets.
- Randomness locality: no sampling in core allocation path; any pseudo-random fill/zero pattern generation is operator-owned (`ZeroTensor`) and deterministic.
- Replay guarantee: replayable given `(replay_token, ir_hash, mode, arena_config, execution_order)`.
- Replay token size: fixed 32 bytes (SHA-256 output), inherited from kernel contract.
- No randomness in core path. Full replayability of layout, zeroing, and physical remapping.

### 0.C Numeric Policy
- All sizes, offsets, alignments, and addresses in uint64.
- No floating-point in allocation path.
- Zeroing policy: `ZeroTensor` writes literal zeros only.
- Optional debug fill: `DebugFillTensor` may write deterministic patterns; forbidden in `confidential` and `regulated` modes.
- Overflow policy: abort on uint64 overflow in offset/size arithmetic.
- Approx-equality: exact integer equality only.
- Normalized exponentials / transcendental functions: N/A for allocator semantics.

### 0.D Ordering and Tie-Break Policy
- Tensors ordered by first definition node_id (earliest wins on ties).
- Logical slots assigned in ascending order (lowest available first).
- Within same birth time: larger tensors first (size-descending heuristic for better packing).
- Secondary tie-break for equal birth and equal size: `tensor_id` lexicographic ascending.

### 0.E Parallel, Concurrency, and Reduction Policy
- Allocation is purely sequential and deterministic.
- Driver-level intra-op parallelism does not affect virtual layout.

### 0.F Environment and Dependency Policy
- Requires UML_Model_IR with complete shape, dtype, and tensor-role hints.
- Depends on execution_order and arena_config.
- Reference runtime: pure Python simulator for E0 verification.
- Dependencies: replay_token and deterministic slot ordering.
- Determinism level: `BITWISE` for slot assignments and logical-address mapping.

### 0.G Operator Manifest
- `Glyphser.TMMU.PrepareMemory`
- `Glyphser.TMMU.PlanMemory`
- `Glyphser.TMMU.ApplyPlan`
- `Glyphser.Model.AnalyzeLiveness`
- `Glyphser.TMMU.AssignLogicalSlots` (new)
- `Glyphser.TMMU.MapToVirtualAddresses` (new)
- `Glyphser.TMMU.ZeroTensor`
- `Glyphser.TMMU.DebugFillTensor`
- `Glyphser.TMMU.CommitExecution`
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- Fully-qualified names: `Glyphser.TMMU.<Name>_v#`

### 0.I Outputs and Metric Schema
- Declared outputs: `tensor_map: dict[tensor_id → {logical_address, arena, logical_slot, size, lifetime}]`, `metrics`
- Minimum metrics: `peak_logical_slots`, `peak_physical_bytes_per_arena`, `memory_reuse_ratio`, `max_live`, `internal_fragmentation_ratio`, `allocation_time_ns`
- Completion status: `success | failed` with deterministic failure codes from 0.K.

### 0.J Spec Lifecycle Governance
- Changes affecting liveness intervals, slot assignment, or logical-address derivation require MAJOR version bump.
- Performance-only implementation changes that preserve outputs/trace semantics require MINOR bump.
- Equivalence target: E0 for slot map and logical-address determinism.

### 0.K Failure and Error Semantics
- Failure codes: `INVALID_IR_SHAPES`, `LIVENESS_CYCLE`, `ADDRESS_COLLISION`, `ALLOCATION_OVERFLOW`, `ARENA_TOO_SMALL`, `ALIGNMENT_VIOLATION`
- `ADDRESS_COLLISION` is unreachable in nominal path with injective arena-offset mapping; it is reserved for corrupted metadata detection.
- Always aborts with full context.

### 0.L Input/Data Provenance
- Relies on ir_dag canonical hash and replay_token.
- All shapes/dtypes/roles fingerprinted.

### 0.M Recommended Presets
- `train_full`: forward + backward (max activation retention)
- `inference`: aggressive reuse
- `remat_enabled`: future selective rematerialization hints

### 0.N Arena Policy (new)
- `parameters`: persistent, no reuse, sequential offsets.
- `activations`: high-reuse interval allocation.
- `gradients`: backward-only, high-reuse.
- Each arena has its own logical-slot space and virtual-address base.

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
- None (stateless; arenas managed by upper TMMU layer).

### I.B Inputs and Hyperparameters
- `ir_dag: UML_Model_IR` (with tensor roles)
- `execution_order: node[]`
- `mode: "forward" | "backward" | "inference"`
- `replay_token: bytes32` (32 bytes, SHA-256)
- `arena_config`: {arena_name → {capacity_bytes, alignment_bytes (default 128), page_size}}

### I.C Constraints and Feasible Set
- All shapes/dtypes known statically.
- Acyclic dataflow.
- Peak live bytes per arena ≤ arena capacity.
- Alias/in-place constraints must be declared in IR metadata and honored by liveness planner.
- Dynamic shapes require either declared shape envelope or deterministic replan trigger policy.

### I.D Transient Variables
- `live_ranges`, `active_set`, `logical_slot_map`, `logical_address_table`, `free_intervals_per_arena` (for size-aware fallback)

### I.E Invariants and Assertions
- No access before birth or after death.
- Live tensors in same logical slot never overlap.
- Base storage slot offsets are unique within arena; views/aliases may overlap by declared alias contract.
- Alignment respected.
- Mathematical guarantee: #logical_slots_per_arena = max simultaneous live tensors in that arena (interval graph optimality).

### II.F Arena and Slot Model (Normative)
- Arena model: each device exposes `{arena_id, base_ptr, size_bytes, alignment_bytes}`.
- Slot model: each allocation emits `{arena_id, slot_offset, size_bytes, alignment, generation}`.
- Pointer derivation: `ptr = base_ptr + slot_offset`.
- Hashes are allowed only for stable tensor identity/fingerprints, never as address source.
- Backend allocation scope:
  - backend direct allocations are forbidden for traced tensors and contract-critical buffers;
  - backend-internal ephemeral scratch is allowed only if it is excluded from trace/certificate semantics and cannot affect deterministic outputs.

### II.G Alias and In-Place Semantics (Normative)
- Shared-storage tensors must declare `alias_group_id`.
- Views must declare `view_descriptor = {base_tensor_uid, byte_offset, byte_length, stride_desc}`.
- In-place writes are allowed only when all are true:
  - `alias_group_refcount == 1`,
  - `saved_for_backward == false`,
  - liveness constraints remain valid for the base storage.
- Alias refcount lifecycle:
  - increment on alias/view creation bound to `alias_group_id`,
  - decrement on deterministic end-of-liveness event for each alias member,
  - storage reuse allowed only when refcount reaches zero.

### II.H Dynamic Shapes and Replan Policy (Normative)
- Dynamic dimensions must declare `shape_envelope` bounds.
- `replan_policy: "ABORT" | "REPLAN_AT_SAFEPOINT"`.
- Replans may occur only at declared safepoints (iteration boundary), must emit trace record with old/new `tmmu_plan_hash`, and checkpoint must store updated plan hash.

### II.I Distributed Sharding Awareness (Normative)
- Plan validity must include `{rank, world_size, shard_spec_hash}`.
- `tmmu_plan_hash` must incorporate rank-local arena layout and global shard specification.
- Planner must support parameter, activation, and optimizer-state sharding contracts.

### II.K Plan Hash (Normative)
- `execution_order_hash = SHA-256(CBOR_CANONICAL(execution_order))`.
- `shard_spec_hash = SHA-256(CBOR_CANONICAL(shard_spec))`, where `shard_spec` is resolved from manifest parallelism/sharding configuration.
- `tmmu_plan_hash = SHA-256(CBOR_CANONICAL(["tmmu_plan", [ir_hash, mode, arena_config_hash, execution_order_hash, rank, world_size, shard_spec_hash, slot_assignment_table, logical_address_table]]))`.
- `replay_token` is `bytes32` and is included in `slot_assignment_table` derivation inputs.

### II.J Resource Ledger Emission (Normative)
- Allocator must emit deterministic resource-ledger counters per step:
  - `bytes_allocated`, `peak_bytes`, `allocation_failures`, `internal_fragmentation_ratio`.
- Quota policy integration:
  - allocator receives `memory_bytes_budget`,
  - on budget breach emits deterministic quota failure and no partial allocation commit.

---

## 3) Initialization

1. Validate IR, shapes, roles, execution_order vs mode.
2. `live_ranges ← AnalyzeLiveness(ir_dag, execution_order, mode)`
3. Classify tensors into arenas based on role/mode.

---

## 4) Operator Manifest

Active operators:
- `Glyphser.TMMU.PrepareMemory`
- `Glyphser.Model.AnalyzeLiveness`
- `Glyphser.TMMU.AssignLogicalSlots`
- `Glyphser.TMMU.MapToVirtualAddresses`
- `Glyphser.TMMU.ZeroTensor`
- `Glyphser.TMMU.DebugFillTensor`
- `Glyphser.TMMU.CommitExecution`
- `Glyphser.Error.Emit`

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

**Operator:** `Glyphser.TMMU.PrepareMemory`  
**Category:** Memory  
**Signature:** `(ir_dag, execution_order, mode, replay_token, arena_config → tensor_map, metrics)`  
**Purity class:** STATEFUL  
**Determinism:** Fully deterministic  
**Definition:** Compatibility wrapper orchestrating `PlanMemory` (PURE) and `ApplyPlan` (STATEFUL) with identical observable outputs to legacy callers.
**Preconditions / Postconditions:** valid IR and arena config; returns deterministic tensor_map/metrics with zeroed handles.  
**Edge cases:** tiny graphs, near-capacity arenas, mixed-role tensors.  
**Numerical considerations:** integer-only offset/address arithmetic with overflow checks.  
**Ordering/tie handling:** birth-time ascending, size-desc tie-break, lowest-slot-first assignment.  
**Complexity note:** O(N log N) worst-case (N=tensors).  
**Failure behavior:** abort with 0.K allocator codes.  
**Dependencies:** PlanMemory, ApplyPlan, AnalyzeLiveness, AssignLogicalSlots, MapToVirtualAddresses, ZeroTensor, CommitExecution.  

**Operator:** `Glyphser.TMMU.PlanMemory`
**Category:** Memory
**Signature:** `(ir_dag, execution_order, mode, arena_config -> tmmu_plan, metrics)`
**Purity class:** PURE
**Determinism:** Fully deterministic
**Definition:** Builds tensor interval set from IR outputs/inputs/persistent buffers, computes births/deaths from execution order, and emits deterministic slot/offset plan with plan hash.

**Operator:** `Glyphser.TMMU.ApplyPlan`
**Category:** Memory
**Signature:** `(tmmu_plan, runtime_arena_handles -> tensor_map, metrics, tmmu_state')`
**Purity class:** STATEFUL
**Determinism:** deterministic
**Definition:** Applies logical `(arena_id, offset_bytes)` plan to runtime pointers, performs zero/fill operations, and commits allocator state.
**Test vectors:** see VII.B chain/residual/large-model slot maps.

**Operator:** `Glyphser.Model.AnalyzeLiveness`  
**Category:** Model  
**Signature:** `(ir_dag, execution_order, mode → live_ranges)`  
**Purity class:** PURE  
**Definition:** Linear pass; backward extends activation lifetimes until gradient use.
If `saved_for_backward=true`, death time is extended through the last backward consumer of the saved tensor/view.
**Preconditions / Postconditions:** valid execution_order and IR references; returns complete live intervals for all tensors.  
**Edge cases:** branched DAG fan-out/fan-in and backward retention boundaries.  
**Numerical considerations:** N/A (graph interval computation).  
**Ordering/tie handling:** deterministic node traversal order.  
**Complexity note:** O(|nodes| + |edges|).  
**Failure behavior:** abort on malformed IR references.  
**Dependencies:** UML_Model_IR schema.  
**Test vectors:** known DAGs with expected intervals.

**Operator:** `Glyphser.TMMU.AssignLogicalSlots` (new)  
**Category:** Memory  
**Signature:** `(live_ranges, arena_config -> logical_slot_assignment: dict[tensor_id -> (arena, logical_slot_id)], slot_size_map: dict[(arena, logical_slot_id) -> uint64], slot_alignment_map: dict[(arena, logical_slot_id) -> uint64])`  
**Purity class:** PURE  
**Definition:** Optimal greedy linear-scan on interval graph per arena (optimal slot count). Each logical slot backing is sized to max tensor assigned to it and emits deterministic `slot_size_map` / `slot_alignment_map` required by virtual mapping.
**Preconditions / Postconditions:** intervals are valid and non-negative; output has no overlapping intervals per slot.  
**Edge cases:** equal birth/death times and sparse arenas.  
**Numerical considerations:** integer interval endpoints only.  
**Ordering/tie handling:** deterministic tie-breaks by birth then size then tensor_id.  
**Complexity note:** O(N log N).  
**Failure behavior:** abort on invalid interval data.  
**Dependencies:** live-range analyzer and arena config.  
**Test vectors:** interval-coloring optimality cases.
**Policy note:** slot-count optimality does not guarantee globally minimal physical bytes under heterogeneous tensor sizes; first-fit deterministic policy may leave additional fragmentation, which is tracked by `internal_fragmentation_ratio`.

**Operator:** `Glyphser.TMMU.MapToVirtualAddresses` (new)  
**Category:** Memory  
**Signature:** `(logical_slot_assignment, arena_config, slot_size_map, slot_alignment_map -> logical_map)`  
**Purity class:** PURE  
**Definition:** For each arena independently, sort slots by `logical_slot_id` ascending and compute aligned offsets by prefix sum: `offset_0=0`, `offset_{k+1}=align_up(offset_k + slot_size_k, align_{k+1})`, where `align_k = max(slot_alignment_map[arena, slot_k], arena_config[arena].alignment_bytes)`. If `slot_alignment_map` entry is missing, default alignment is `arena_config[arena].alignment_bytes`. Emit logical addresses as `(arena_id, offset_bytes)`; runtime resolves to physical pointers out-of-band.
**Preconditions / Postconditions:** logical slots assigned; output addresses unique per `(arena, slot)`.  
**Edge cases:** large slot cardinality and arena name collisions (disallowed).  
**Numerical considerations:** uint64 offset arithmetic with overflow checks; no hash truncation/collision path.  
**Ordering/tie handling:** deterministic map key order for serialization.  
**Complexity note:** O(slots).  
**Failure behavior:** abort on arena overflow or alignment violation.  
**Dependencies:** deterministic ordering and arena config.  
**Test vectors:** fixed arena config + slot maps -> exact logical map.

**Operator:** `Glyphser.TMMU.ZeroTensor`  
**Category:** Memory  
**Signature:** `(logical_address, size_bytes -> ok)` (driver primitive)  
**Purity class:** STATEFUL  
**Definition:** Deterministic zero-fill.
**Preconditions / Postconditions:** address is valid and writable; tensor contents are zeroed.  
**Edge cases:** repeated zeroing and page boundary segments.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** called in deterministic tensor-map order.  
**Complexity note:** O(size of tensor backing).  
**Failure behavior:** abort on invalid address/write failure.  
**Dependencies:** driver memory primitive.  
**Test vectors:** zero verification across varied tensor sizes.

**Operator:** `Glyphser.TMMU.DebugFillTensor`  
**Category:** Memory  
**Signature:** `(logical_address, pattern_seed -> ok)`  
**Purity class:** STATEFUL  
**Definition:** Deterministic debug pattern fill for allocator diagnostics only.
**Preconditions / Postconditions:** allowed only in non-confidential and non-regulated modes.  
**Edge cases:** repeated fill operations.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic tensor-map order.  
**Complexity note:** O(size of tensor backing).  
**Failure behavior:** abort on invalid address/mode violation.  
**Dependencies:** driver memory primitive and execution mode.

**Operator:** `Glyphser.TMMU.CommitExecution`  
**Category:** Memory  
**Signature:** `(() -> tmmu_state')`  
**Purity class:** STATEFUL  
**Definition:** Executes deterministic synchronization barriers, commits arena visibility state for downstream consumers, and seals per-batch memory metadata for replay/audit consistency.
**Preconditions / Postconditions:** pending memory operations completed; committed state is durable for next stage.  
**Edge cases:** no-op batch and single-arena execution.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic barrier ordering across arenas.  
**Complexity note:** O(number of active arenas).  
**Failure behavior:** abort on synchronization failure.  
**Dependencies:** runtime barrier and allocator metadata state.  
**Test vectors:** repeated commit idempotence and deterministic state hash.

---

## 6) Procedure

```text
1. live_ranges ← AnalyzeLiveness(ir_dag, execution_order, mode)
   # Mode-aware lifetime extension for backward activations/gradients

2. logical_slots, slot_size_map, slot_alignment_map ← AssignLogicalSlots(live_ranges, arena_config)
   # Per-arena linear-scan (optimal for interval graphs):
   #   - Sort tensors by birth time, then size descending
   #   - Maintain active_slots set (bitset or min-heap of used slots)
   #   - For each tensor: expire ended slots, assign lowest unused logical_slot
   #   - Emit slot_size_map[(arena, slot)] = max(required_tensor_bytes for tensors in slot)
   #   - Emit slot_alignment_map[(arena, slot)] = max(required_tensor_alignment, arena_config[arena].alignment_bytes)

3. logical_map ← MapToVirtualAddresses(logical_slots, arena_config, slot_size_map, slot_alignment_map)
   # Per arena: deterministic slot order by logical_slot_id
   # offset_0 = 0
   # offset_{k+1} = align_up(offset_k + slot_size_k, align_{k+1})
   # va(slot_k) = arena_base[arena] + offset_k

4. tensor_map ← {}
   tensor_intervals_sorted ← tensors sorted deterministically by `tensor_id` ascending
   for tensor in tensor_intervals_sorted:   # tensors, not nodes
       (arena, slot) ← logical_slots[tensor.id]
       logical_addr ← logical_map[(arena, slot)]  # (arena_id, offset_bytes)
       size ← compute_bytes(tensor.shape, tensor.dtype)
       tensor_map[tensor.id] ← {logical_address: logical_addr, arena, logical_slot: slot, size, lifetime: live_ranges[tensor.id], alignment: arena_config[arena].alignment}

5. for each tensor in tensor_map:
       ZeroTensor(tensor_map[tensor_id].logical_address, tensor_map[tensor_id].size)
       # DebugFillTensor is optional and forbidden in confidential/regulated modes.

6. metrics ← ComputeMetrics(live_ranges, logical_slots, logical_map)
   # Includes per-arena peak, reuse_ratio = 1 - (slots_used / total_tensors), fragmentation

7. tmmu_state' ← CommitExecution()
8. return tensor_map, metrics
```

**Scalability & Algorithmic Guarantees (upgraded):**
- Time: O(N log N) worst-case with heap/interval-tree for active set (N = #tensors)
- Space: O(max live) 
- Mathematical optimality: #logical_slots = max live tensors per arena (interval graphs are perfect → greedy coloring is exact)
- This optimality applies to slot count only; total allocated bytes after slot sizing/alignment are heuristic and may be suboptimal.
- Memory reuse ratio typically >95% on transformer graphs
- Physical-byte optimality is not guaranteed for heterogeneous sizes under first-fit; this is an explicit tradeoff for deterministic reproducibility and slot optimality.
- Supports 100B+ models via compact per-slot backing + huge virtual address space (2^48+)
- Alignment & padding enforced per arena
- Future-proof: easy extension to remat, paging, size-class bucketing

---

## 7) Trace & Metrics

### Logging rule
Each allocation run emits deterministic per-tensor allocation records and one deterministic summary record.

### Trace schema
- `allocation_header`: ir_hash, mode, replay_token_prefix, per-arena config
- `tensor`: tensor_id, arena, logical_slot, logical_address, size, live_range, bytes
- `summary`: peak_bytes_per_arena, total_logical_slots, reuse_ratio, fragmentation_pct

### Metric schema
- `peak_tmmu_usage_per_arena`, `memory_reuse_ratio`, `activation_retention_ratio`, `allocation_time_ns`, `max_live`, `internal_fragmentation_ratio`

### Comparability guarantee
Two allocation runs are comparable iff `ir_hash`, arena config, replay token context, trace schema, and metric schema are identical.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
- All tensors aligned and slotted without live overlap.
- #slots == max live per arena.
- Backward lifetimes correctly extended.
- Logical-address uniqueness & determinism.

#### VII.B Operator test vectors (mandatory)
- Linear chain → perfect reuse (1 slot)
- Residual blocks → optimal coloring
- GPT-2 / Llama-scale → high reuse + alignment validation

#### VII.C Golden traces (mandatory)
- Match reference Python simulator (E0) for all presets/modes/seeds.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- **E0** required for any change to liveness, slot assignment, or logical-address computation.
- **E1** allowed for heuristics (e.g., sorting order).

#### VIII.B Allowed refactor categories
- Graph-coloring variants, ILP solver (if E0 preserved), rematerialization planner, hierarchical arenas.

#### VIII.C Equivalence test procedure (mandatory)
- Identical logical addresses, logical slots, and live sets on golden graphs (10 seeds × all presets × 3 modes).

---

## 10) Checkpoint/Restore

### Checkpoint contents
- logical_slot_assignment + live_ranges + metrics (compact).

### Serialization
- CBOR, deterministic ordering (sorted by node_id).

### Restore semantics
- Same replay_token → identical layout.
- Physical backing re-mappable by driver.

### Dynamic/Alias Policy
- IR must declare:
  - `alias_group_id` for shared-storage views,
  - `must_not_alias` constraints,
  - `in_place_write` markers extending live ranges,
  - `saved_for_backward` markers.
- Replan key: `(shape_envelope_hash, mode, arena_config_hash)`; if runtime shape exits envelope, deterministic replan is required and logged.
