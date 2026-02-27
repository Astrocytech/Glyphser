# Universal Machine Learning Operating System — ModelIR Executor
**EQC Compliance:** This specification follows EquationCode (EQC) v1.1 merged single-file format (Option A): 10 top-level sections, global semantics first, operator-owned math, control-flow-only procedure, deterministic contracts, and replayable stochasticity.

**Algorithm:** `Glyphser.Model.ModelIR_Executor`  
**Purpose (1 sentence):** Deterministically execute any valid UML_Model_IR DAG on a contract-validated backend driver using TMMU-managed memory with strict topological ordering, static liveness analysis for slot reuse, **mode-aware forward/reverse scheduling**, and full support for forward/backward/inference passes, guaranteeing E0/E1 reproducibility per declared adapter/hardware tier while scaling to 100 B+ parameter models.  
**Spec Version:** `Glyphser.Model.ModelIR_Executor` | 2026-02-18 | Authors: Olejar Damir (with EQC team improvements)  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Declarative neural-network graph execution with memory isolation and bit-identical reproducibility.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `Glyphser.Model.ModelIR_Executor`
- **Purpose (1 sentence):** Execute UML_Model_IR DAGs deterministically on validated drivers with TMMU memory management.
- **Spec Version:** `Glyphser.Model.ModelIR_Executor` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Scalable deterministic ML computation graph execution.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Not an optimization operator.
- Primary guarantee: deterministic critical-path outputs for identical `(ir_dag, theta, inputs, mode, replay_token, backend_binary_hash, driver_runtime_fingerprint_hash)` under a declared adapter/hardware determinism tier.
- Comparison rule: exact tensor equality on binary64 critical reductions; EPS_EQ tolerance on compute_dtype paths.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` inherited from kernel master RNG (no direct draws in core path).
- PRNG family: Philox4x32-10 (only inside custom operators/driver primitives that declare consumption).
- Randomness locality: strictly inside registered custom operators or backend primitives that explicitly declare RNG consumption through `DispatchPrimitive`.
- Replay guarantee: fully replayable given `(ir_hash, theta_hash, input_hash, mode, replay_token, tmmu_context, backend_binary_hash, driver_runtime_fingerprint_hash)`.
- Replay token contribution: `modelir_replay_t = SHA-256(CBOR_CANONICAL(["modelir_executor", [kernel_replay_token, ir_hash, mode, uint64(global_position)]]))`.
- Proof-carrying IR fields:
  - `ir_schema_hash`
  - `ir_operator_set_hash`
  - `primitive_semantics_hash_set`
- Determinism tier contract: E0 only within same adapter build + deterministic kernel set + fixed math flags; E1 across broader hardware/driver classes.

### 0.C Numeric Policy
- Critical reductions/gradients/norms/fingerprints: IEEE-754 binary64 with Kahan or pairwise summation in ascending node_id order.
- All other computations: manifest.compute_dtype (float32 default).
- Rounding: round-to-nearest ties-to-even.
- Fast-math: forbidden.
- NaN/Inf policy: inherited from kernel 0.A/0.K (rank as +Inf, abort on critical paths).
- Normalized exponentials: stable log-sum-exp required for softmax/log-probability primitives.
- Approx-equality: `a ≈ b` iff `|a - b| <= EPS_EQ` on non-bitwise paths.

### 0.D Ordering and Tie-Break Policy
- Index base: 0-based.
- Execution order: strict topological order with stable sort by node_id (lowest node_id wins on ties). **For backward mode: reversed topological order (guarantees correct gradient propagation order).**
- Tensor reductions: ascending flat index or node_id order.
- Backward ordering contract: execution follows topological order of the explicit gradient dependency graph (`grad_edges`); plain reverse-forward order is valid only when equivalent to `grad_edges` order.

### 0.E Parallel, Concurrency, and Reduction Policy
- Driver handles intra-op parallelism (must be deterministic per Contract.Validate).
- Inter-node execution: sequential topological order (no concurrent nodes unless driver proves independence under contract).
- Reductions: fixed ascending-index tree order per kernel 0.E.

### 0.F Environment and Dependency Policy
- Requires loaded compliant backend driver (via Glyphser.Backend.LoadDriver) and active TMMU.
- Reference runtime: CPU reference driver for E0 verification.
- Dependencies: UML_Model_IR schema (0.Y of kernel), registered custom operators, TMMU arena.
- **Backward-mode requirement:** ir_dag contains the same nodes as forward but DispatchPrimitive uses mode="backward" to invoke gradient kernels; execution order must follow explicit gradient dependency order.
- Determinism level: `BITWISE` for critical tensors/fingerprints, `TOLERANCE` for non-critical compute_dtype paths.

### 0.G Operator Manifest
- `Glyphser.Model.ModelIR_Executor`
- `Glyphser.Model.TopoSortNodes`
- `Glyphser.Model.BuildGradDependencyOrder`
- `Glyphser.Model.DispatchPrimitive`
- `Glyphser.Model.CollectGradients`
- `Glyphser.TMMU.PrepareMemory` (includes static liveness + deterministic slot assignment)
- `Glyphser.Fingerprint.StateFingerprint`
- `Glyphser.TMMU.CommitExecution`
- `Glyphser.Contract.Validate`
- `Glyphser.Error.Emit`

### 0.H Namespacing and Packaging
- Fully-qualified names: `Glyphser.Model.<Name>_v#`

### 0.I Outputs and Metric Schema
- Declared outputs: `(outputs: tensor_map, grads?: tensor_map, execution_fp, tmmu_state_next, rng_state_next)`
- Minimum metrics: `nodes_executed`, `mode`, `memory_reuse_ratio`, `peak_tmmu_usage`, `execution_fp`
- Completion status: `success | failed` with deterministic reason codes.

### 0.J Spec Lifecycle Governance
- Any change to execution ordering, dispatch semantics, or memory-layout determinism requires MAJOR version bump.
- Performance-only optimizations preserving outputs/trace semantics require MINOR bump.
- Equivalence target: E0 for critical paths and execution trace.

### 0.K Failure and Error Semantics
- Global error model: abort-only
- Failure codes: `INVALID_IR`, `CYCLE_DETECTED`, `SHAPE_MISMATCH`, `PRIMITIVE_UNSUPPORTED`, `TMMU_ALLOCATION_FAILURE`, `CONTRACT_VIOLATION`
- Failure record fields: `t`, `failure_code`, `node_id`, `modelir_replay_t`

### 0.L Input/Data Provenance
- IR must carry canonical `ir_hash`; all input tensors must be TMMU-resident and fingerprinted.

### 0.M Recommended Presets
- `forward_train`: forward pass + activation saving
- `backward_train`: **reverse topological gradient propagation** (reversed execution_order + gradient-kernel dispatch)
- `inference`: forward-only with no grad tracking

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
- Executor-local state is stateless per call; mutable tensor residency/state is externalized in `tmmu_context` and returned as `tmmu_state'`.

### I.B Inputs and Hyperparameters
- `ir_dag: UML_Model_IR` (nodes with `node_id`, `instr`, `params`, `inputs`, `shape_in/out`)
- `theta: dict` (parameter tensors)
- `input_data: tensor_map` (for input nodes)
- `mode: "forward" | "backward" | "inference"`
- `loss_outputs: array<(node_id, output_idx)>` (required in backward mode)
- `seed_rule: "UNIT_SCALAR" | "PROVIDED_GRADIENTS"`
- `replay_token: bytes32`
- `tmmu_context`
- `arena_config` (deterministic memory arena configuration passed to TMMU)
- `rng_state` (kernel-provided deterministic RNG stream state)

### I.C Constraints and Feasible Set
- DAG acyclic and shapes statically known/inferable.
- All `instr` supported by driver or registered custom.
- `global_batch_size % world_size == 0` (inherited from kernel).
- **Backward-mode invariant:** every node must have a corresponding gradient implementation in the driver.

### I.D Transient Variables
- `execution_order`, `tensor_map`, `grad_map` (backward only), `rng_state_work`

### I.E Invariants and Assertions
- Topological order respected (forward order for forward/infer; explicit gradient dependency order for backward).
- Every node input available before dispatch.
- All allocated tensors zeroed by TMMU before first write.
- Critical reductions performed in binary64 with fixed order.
- TMMU deterministic virtual addressing (delegated to `docs/layer2-specs/TMMU-Allocation.md` contract).
- Backward adjoint invariants:
  - each differentiable tensor has a declared `grad_slot`,
  - all grad slots are zero-initialized at backward start,
  - terminal loss/output gradient seed follows declared `seed_rule`,
  - multi-parent gradient contributions are accumulated by sorting contributions on `(consumer_node_pos, edge_id)` and reducing in fixed order.

### II.F IR Identity and Hash Binding (Normative)
- `ir_hash` definition:
  - validate `ir_object` against declared IR schema,
  - canonicalize as `ir_cbor = CBOR_CANONICAL(ir_object)`,
  - compute `ir_hash = SHA-256(ir_cbor)`.
- `ir_schema_hash` must be embedded in `ir_object`; therefore `ir_hash` commits both graph content and schema identity.
- Cross-artifact binding rule:
  - execution trace, checkpoint header, and execution certificate must carry the same `ir_hash` for a run.

---

## 3) Initialization

1. `Contract.Validate(ir_dag, driver, mode)`
2. `execution_order ← Glyphser.Model.TopoSortNodes(ir_dag)`
3. **if mode == "backward":**
   - **`backward_order, reverse_equivalent_flag ← Glyphser.Model.BuildGradDependencyOrder(ir_dag, execution_order)`**
   - **if `reverse_equivalent_flag == 1`: `execution_order ← reversed(execution_order)` else `execution_order ← backward_order`**
4. `tensor_map ← Glyphser.TMMU.PrepareMemory(ir_dag, execution_order, mode, replay_token, arena_config)` (static liveness + zeroing + deterministic slot reuse; mode-aware activation saving for backward)

---

## 4) Operator Manifest

Active operators:
- `Glyphser.Model.ModelIR_Executor`
- `Glyphser.Model.TopoSortNodes`
- `Glyphser.Model.BuildGradDependencyOrder`
- `Glyphser.Model.DispatchPrimitive`
- `Glyphser.Model.CollectGradients`
- `Glyphser.TMMU.PrepareMemory`
- `Glyphser.Fingerprint.StateFingerprint`
- `Glyphser.TMMU.CommitExecution`
- `Glyphser.Contract.Validate`
- `Glyphser.Error.Emit`

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.

**Operator:** `Glyphser.Model.ModelIR_Executor`  
**Category:** Model  
**Signature:** `(ir_dag, theta, input_data, mode, replay_token, tmmu_context, rng_state → outputs, grads?, execution_fp, tmmu_state_next, rng_state_next)`  
**Purity class:** STATEFUL (TMMU/driver)  
**Determinism:** deterministic  
**Definition:** Executes full pass on UML_Model_IR DAG. Guarantees deterministic layout plans and critical outputs within the declared adapter/hardware determinism tier (E0/E1 contract). **Mode-aware scheduling uses explicit gradient dependency order for backward.**
**Preconditions / Postconditions:** validated IR/driver contract; outputs and optional gradients returned with committed TMMU state.  
**Edge cases:** empty DAG, single-node DAG, backward on non-differentiable nodes.  
**Numerical considerations:** binary64 critical-path reductions with deterministic ordering.  
**Ordering/tie handling:** strict topological order; stable node_id tie-break; backward uses deterministic gradient dependency order (reverse-forward only when proven equivalent).  
**Complexity note:** O(|nodes| + |edges|) dispatch path after initialization.  
**Failure behavior:** abort on 0.K failure codes.  
**Dependencies:** TopoSortNodes, DispatchPrimitive, CollectGradients, PrepareMemory, Glyphser.Fingerprint.StateFingerprint, CommitExecution.  
**Test vectors:** see VII.B tiny DAG forward/backward/inference checks.

**Operator:** `Glyphser.Model.TopoSortNodes`  
**Category:** Model  
**Signature:** `(ir_dag → execution_order: node[])`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Topological sort (Kahn/DFS) with stable tie-break by lowest node_id. Detects cycles. (Reversal for backward performed by caller/executor.)
**Preconditions / Postconditions:** input graph is declared DAG schema; output is deterministic topological ordering.  
**Edge cases:** disconnected DAG components, single node.  
**Numerical considerations:** N/A (graph-only operation).  
**Ordering/tie handling:** stable node_id ascending tie-break.  
**Complexity note:** O(|nodes| + |edges|).  
**Failure behavior:** `CYCLE_DETECTED` abort on non-DAG graph.  
**Dependencies:** IR schema validation.  
**Test vectors:** cycle detection and deterministic ordering checks.

**Operator:** `Glyphser.Model.BuildGradDependencyOrder`
**Category:** Model
**Signature:** `(ir_dag, forward_execution_order -> backward_execution_order: node[], reverse_equivalent_flag: {0,1})`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Builds a topological order over explicit gradient dependency graph (`grad_edges`, or default reverse forward-order edges when `grad_edges` absent). `reverse_equivalent_flag` is `1` only when `reversed(forward_execution_order)` is a valid topological order for the gradient dependency graph; otherwise `0` and `backward_execution_order` MUST be used.

**Operator:** `Glyphser.Model.DispatchPrimitive`  
**Category:** Model  
**Signature:** `(node, tensor_map, theta, mode, tmmu_context, rng_state -> updated_tensor_map, rng_state_next)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic (driver contract)  
**Definition:** Resolves input handles, dispatches driver primitive for `node.instr` **(fwd or grad variant based on mode)**, writes output to TMMU-allocated slot, validates shapes, and forwards a deterministic RNG sub-stream for primitives/custom ops that declare randomness.
Each primitive MUST declare deterministic RNG consumption (`rng_draws_per_invocation`); if zero, `rng_state_next == rng_state`.
`tmmu_context` is an opaque runtime handle provided by the TMMU layer for deterministic memory access/slot resolution.
**Preconditions / Postconditions:** all input handles exist; output handle written with validated shape/dtype; RNG state advanced only by declared primitive RNG consumption.  
**Edge cases:** unsupported primitive, custom op fallback, zero-size tensors.  
**Numerical considerations:** primitive-specific binary64 critical paths enforced by driver contract.  
**Ordering/tie handling:** follows provided execution order exactly.  
**Complexity note:** primitive-dependent; dispatch overhead O(1) per node.  
**Failure behavior:** `PRIMITIVE_UNSUPPORTED`/`SHAPE_MISMATCH`/`CONTRACT_VIOLATION` abort.  
**Dependencies:** backend driver dispatch table, TMMU handles, kernel RNG ownership contract.  
**Test vectors:** per-primitive deterministic forward/backward outputs.

**Operator:** `Glyphser.Model.CollectGradients`  
**Category:** Model  
**Signature:** `(tensor_map, ir_dag -> grads: tensor_map)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** After backward pass, aggregates all parameter gradients (from dedicated grad slots or accumulated in-place) into a clean grads dict. When multiple contributors exist, accumulation order is deterministic by `producer_node_id` ascending using binary64 compensated summation.
**Preconditions / Postconditions:** backward artifacts present; returned grads aligned to parameter registration order.  
**Edge cases:** sparse gradients, frozen parameters.  
**Numerical considerations:** deterministic accumulation order for merged gradients.  
**Ordering/tie handling:** parameter order from model registration.  
**Complexity note:** O(|theta|).  
**Failure behavior:** abort on missing gradient tensor or dtype mismatch.  
**Dependencies:** IR parameter metadata and tensor map.  
**Test vectors:** gradient extraction on known tiny models.

**Operator:** `Glyphser.TMMU.PrepareMemory`  
**Category:** Memory  
**Signature:** `(ir_dag, execution_order, mode, replay_token, arena_config -> tensor_map)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** Performs static liveness analysis on IR; delegates virtual addressing to the versioned TMMU allocation contract; zeros all tensors; prepares reuse schedule. **Mode-aware: reserves extra slots for activations only when backward is requested.**
**Preconditions / Postconditions:** valid TMMU context and arena config; tensor handles are ready before dispatch.  
**Edge cases:** memory pressure near arena cap.  
**Numerical considerations:** N/A (address arithmetic in integer space).  
**Ordering/tie handling:** deterministic slot assignment order from liveness plan.  
**Complexity note:** O(|nodes| log |nodes|) worst-case for allocation planning.  
**Failure behavior:** abort on allocation failure/alignment violations.  
**Dependencies:** `Glyphser.TMMU` allocation operators and replay token context.  
**Test vectors:** deterministic slot map across repeated runs.

---

**Operator:** `Glyphser.Contract.Validate`  
**Category:** Contract  
**Signature:** `(ir_dag, driver, mode -> contract_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Verifies IR schema, primitive coverage, determinism requirements, and mode constraints before execution.

**Operator:** `Glyphser.Fingerprint.StateFingerprint`  
**Category:** Observability  
**Signature:** `(tensor_map -> execution_fp)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Computes canonical binary64 fingerprint over declared critical tensors using deterministic ordering.

**Operator:** `Glyphser.TMMU.CommitExecution`  
**Category:** Memory  
**Signature:** `(tmmu_context -> tmmu_state_next)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** Finalizes memory barriers/ownership and commits deterministic TMMU state after batch execution.

## 6) Procedure

```text
1. Contract.Validate(ir_dag, driver, mode)
2. execution_order ← TopoSortNodes(ir_dag)
3. if mode == "backward":
       backward_order, reverse_equivalent_flag <- BuildGradDependencyOrder(ir_dag, execution_order)
       if reverse_equivalent_flag == 1:
           execution_order <- reversed(execution_order)
       else:
           execution_order <- backward_order
4. tensor_map ← TMMU.PrepareMemory(ir_dag, execution_order, mode, replay_token, arena_config)  # static liveness + zeroing + slot reuse (mode-aware)

5. rng_state_work <- rng_state
6. for node in execution_order:
       tensor_map, rng_state_work <- DispatchPrimitive(node, tensor_map, theta, mode, tmmu_context, rng_state_work)

7. if mode == "backward":
       grads ← CollectGradients(tensor_map, ir_dag)  # now explicitly defined operator

8. outputs ← extract_output_nodes(tensor_map, ir_dag)
9. execution_fp ← Glyphser.Fingerprint.StateFingerprint(tensor_map)  # critical tensors only
10. TMMU.CommitExecution()  # sync barriers for isolation
11. return outputs, grads?, execution_fp, tmmu_state_next, rng_state_work
```

**Scalability & Algorithmic Guarantees:**
- Time: O(|nodes| + |edges|) per execution after O(|nodes|) liveness prep.
- Memory: O(live set size) via static liveness + deterministic slot reuse (enables 100 B+ models on fixed arena).
- **Backward pass now algorithmically correct** (reverse topological order + mode-aware dispatch).
- Exact bijection with CPU reference driver on critical paths (E0).
- Fully supports streaming/large-batch via TMMU virtual addressing; no O(N) storage beyond live tensors.

---

## 7) Trace & Metrics

### Logging rule
Each invocation emits deterministic node-level trace records in execution order and a final summary record.

### Trace schema (minimum required)
- `run_header`: `ir_hash`, `mode`, `backend_binary_hash`, `driver_runtime_fingerprint_hash`, `tmmu_arena_size`
- `node`: `node_id`, `instr`, `shape`, `dtype`, `dispatch_success`
- `run_end`: `execution_fp`, `memory_peak`, `reuse_ratio`, `nodes_executed`
- critical reductions set (normative minimum): `loss_total`, `grad_norm`, and tensors used by `StateFingerprint`.

### Metric schema
- `nodes_executed`, `memory_reuse_ratio`, `peak_tmmu_usage`, `execution_fp`

### Comparability guarantee
Two executions are comparable iff `ir_hash`, determinism tier, backend/profile hashes, trace schema, and metric schema are identical.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
- DAG acyclicity, shape propagation totality, primitive coverage, topological determinism, TMMU contract adherence, **backward-order correctness**.

#### VII.B Operator test vectors (mandatory)
- Tiny linear/residual/transformer DAGs → exact binary64 match vs reference driver.
- Backward pass gradient verification within EPS_EQ (now tested with explicit reverse ordering).

#### VII.C Golden traces (mandatory)
- Full forward/backward/inference on all kernel presets (ResNet, ViT, GPT) across drivers; E0 critical-path match.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- **E0** required for any change affecting critical-path tensors or execution order.
- **E1** allowed for non-critical memory optimizations.

#### VIII.B Allowed refactor categories
- Alternative topological algorithms (must preserve stable node_id order + reverse for backward).
- Advanced static liveness / fusion / **rematerialization heuristics** (via driver contract; preserves E0).
- Kernel-fusion extensions (preserves E0).

#### VIII.C Equivalence test procedure (mandatory)
- 10 seeds × all presets × 3 modes.
- Exact match on gradients/losses/fingerprints in binary64; statistical test on non-critical paths.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- Stateless executor; relies on kernel checkpoint of `ir_dag`, `theta`, and TMMU state.

### Serialization
- TMMU state via deterministic CBOR (fixed order).

### Restore semantics
- Identical execution sequence on restore (same replay_token → same slot assignments).
- Mid-pass restore not supported (atomic per-batch execution).
- Parameter ownership note: `theta` is passed by reference and may be mutated by backend primitives/gradient buffers under contract; callers must treat post-call `theta` as authoritative state.
