# Universal Machine Learning Operating System (Glyphser) v3.22-OS
**EQC Compliance:** This specification follows the merged single-file format of EquationCode (EQC) v1.1 (Option A) with the required 10 top-level sections and all mandatory invariants (global semantics first, control-flow-only procedure, versioned operators, purity/RNG contracts, total state updates, trace schema, equivalence levels, lint rules, checkpoint replay guarantees).

**Algorithm:** Deterministic training OS kernel with operator contracts, namespace isolation, and hardware attestation.  
**Purpose (1 sentence):** Execute declarative machine learning training, evaluation, inference, and confidential operations under contract-enforced determinism, namespace isolation, hardware-rooted attestation, and verifiable provenance.  
**Spec Version:** Glyphser-v3.22-OS | 2026-02-17 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Reproducible neural-network training, evaluation, inference, and confidential lifecycle management.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** Deterministic training OS kernel with operator contracts, namespace isolation, and hardware attestation.
- **Purpose (1 sentence):** Execute declarative machine learning training, evaluation, inference, and confidential operations under contract-enforced determinism, namespace isolation, hardware-rooted attestation, and verifiable provenance.
- **Spec Version:** Glyphser-v3.22-OS | 2026-02-17 | Authors: Olejar Damir
- **Domain / Problem Class:** Reproducible neural-network training, evaluation, inference, and confidential lifecycle management.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: `a ≼ b ⇔ a ≤ b + EPS_EQ`
- `EPS_EQ = 1e-10` (float64)
- Invalid objective policy: NaN/±Inf ranked as `+Inf`; mark `INVALID_OBJECTIVE`; do not apply update; emit deterministic failure record; abort (0.K).

### 0.B Reproducibility Contract
- Default reproducibility class: `R1 (statistical)`
- `R0` only for reference single-process CPU golden traces
- Seed space: `seed ∈ {0..2^64-1}`
- PRNG family: Philox4x32-10
- Single master stream with fixed sub-stream offsets: `init`, `cluster`, `misc`
- Randomness locality: all sampling occurs **only inside operators**
- Replay guarantee: replayable given `(seed, PRNG family, numeric policy, ordering policy, parallel policy, environment policy)`
- Replay token: `replay_token = SHA-256(CBOR_CANONICAL(["replay_token", [spec_version, policy_bundle_hash, env_manifest_hash, operator_contracts_root_hash, determinism_profile_hash, driver_runtime_fingerprint_hash, uint64(seed)]]))`
- `env_manifest_hash` is defined normatively in `docs/layer1-foundation/Environment-Manifest.md` (`runtime_env_hash` alias allowed in checkpoint contracts).
- Replay context must also bind:
  - `sampler_config_hash`,
  - `tmmu_plan_hash`,
  - `dp_accountant_state_hash`,
  - `operator_contracts_root_hash`,
  - `determinism_profile_hash`,
  - backend runtime fingerprint.
- Canonical hash/input encoding rule (global): all hash inputs are domain-separated CBOR arrays; strings encoded UTF-8; integers encoded as unsigned big-endian logical values via CBOR major type.
- Hash primitives policy (global, normative):
  - contract-critical digests MUST use `SHA-256(CBOR_CANONICAL(...))`,
  - domain-separation tag is required as first CBOR array element,
  - digest slicing (e.g., `[0:16]`) must use leftmost bytes,
  - digest-to-uint conversion uses big-endian interpretation.

### 0.C Numeric Policy
- Core arithmetic (loss, metrics, termination, fingerprints, gradient norms, DP accounting, critical reductions): IEEE-754 binary64 with deterministic ascending-index order and EPS guards.
- Model parameters, optimizer state, intermediates, non-critical computations: manifest.compute_dtype (float32 default).
- Critical reductions and fingerprints: binary64, deterministic ascending-index order
- All reductions (including all-reduce, gradient norm, loss summation) use Kahan compensated summation or pairwise tree reduction in binary64 with fixed ascending-index order; E0 bitwise guarantees apply within a fixed `(world_size, collective algorithm, rank order, driver build, math flags)` equivalence class.
- Rounding mode: round-to-nearest ties-to-even
- Fast-math: forbidden
- Constants: `EPS_EQ = 1e-10`, `EPS_DENOM = 1e-12`, `EPS_PROB = 1e-15`
- Clamps: `exp` argument `[-80, 80]`; denominator `max(den, EPS_DENOM)`; probabilities `[EPS_PROB, 1]` then renormalize
- NaN/Inf policy: NaN/±Inf ranked as `+Inf` (see 0.A); abort per 0.K on critical paths
- Normalized exponentials: stable log-sum-exp required in all softmax / log-probability paths
- Approx-equality: `a ≈ b` iff `|a - b| ≤ EPS_EQ`
- Counter overflow policy: `t`, `current_step`, `operator_seq`, and all uint64 counters MUST fail-fast on overflow (`COUNTER_OVERFLOW`); wraparound is forbidden.

### 0.D Ordering and Tie-Break Policy
- Index base: `0-based`
- Stable sort required
- Ties: lowest index wins
- Fixed action order: `["optimize", "eval", "infer", "switch"]`

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel reductions: fixed 256-element chunks in ascending global index
- Rank aggregation: ascending rank order
- `world_size > 1` requires deterministic collectives and fixed ordering
- Collective algorithm rule (normative): ring all-reduce with ascending-rank send/recv order and fixed chunk partitioning; reduction accumulation uses binary64 Kahan summation in deterministic chunk order.

### 0.F Environment and Dependency Policy
- Each backend driver (loaded via `Glyphser.Backend.LoadDriver`) must implement deterministic forward/backward passes with fixed ascending-index reduction order, deterministic collectives (all-reduce, broadcast) using ascending-rank ring topology, RNG forwarding from kernel master streams with declared offsets, exact operator contracts for all dispatched primitives, and must pass the mandatory ReproducibilityTest suite. The suite requires E0 equivalence within a declared backend/hardware equivalence class (same build/profile), and E1 vs certified CPU reference on larger workloads. Driver verification (including binary/manifest hash check) is mandatory inside `Contract.Validate` before any dispatch.
- Driver interface contract (mandatory for LoadDriver): Implements Forward/Backward/Inference.RunBatch on UML_Model_IR DAG using only deterministic primitives; no exposed user-callable loops; supports memory-zeroing hooks, TMMU allocation/liveness hints, and TEE quote collection; declares exact op-to-primitive mapping. Passes mandatory ReproducibilityTest suite (E0 on tiny graphs vs certified CPU reference in binary64; E1 on larger workloads) before dispatch. In regulated mode only drivers from the configured signed registry are accepted.
- Determinism level: `BITWISE` for critical observables (`loss_total`, `grad_norm`, fingerprints, `state_fp`) within a declared adapter/hardware equivalence class; `TOLERANCE` for raw model parameters.
- `state_fp` canonicalization rule: compute from quantized parameter view `q(theta)=round(theta*2^24)/2^24` in binary64 with fixed ordering, so tolerance-level parameter drift does not violate fingerprint comparability policy.

### 0.G Operator Manifest
Active operator wiring is declared in section `4) Operator Manifest`.

### 0.H Namespacing and Packaging
- Fully-qualified names: `Glyphser.<Category>.<Name>_v#`
- Sidecar mapping required: operator -> module/function
- Normative naming rule: all operators MUST match `Glyphser.<subsystem>.<name>_v<integer>`; flat operators are forbidden.

### 0.I Outputs and Metric Schema
- Declared outputs: `theta_final`, `trace`, `checkpoint`, `tape_digest`, `training_certificate`
- Minimum metric schema: `loss_total`, `grad_norm`, `functional_fp`
- Completion status: `success | terminated | failed` with deterministic reason codes.

### 0.J Spec Lifecycle Governance
Reproducibility-breaking changes require MAJOR bump (vX.Y.Z → v(X+1).0.0).  
Deprecations replace via manifest wiring only.  
Equivalence target for any change: E1 (metric-equivalent) minimum, E0 (trace-equivalent) for kernel or attestation changes.  
Migration: update manifest operator versions and replay_token.

### 0.K Failure and Error Semantics
- Global error model: abort-only
- Final failure record includes: `t`, `failure_code`, `failure_operator`, `replay_token`, `rng_fingerprint_t`, `state_fp_t`

### 0.L Input/Data Provenance
- Dataset id/version/hash mandatory
- Strict parsing and immutable dataset registration mandatory

### 0.M Declarative Configuration
- YAML config mandatory input path
- Canonical JSON serialization before hashing

### 0.N Layered Operating-System Architecture
- Layer ordering:
  - Kernel (VI procedure + operator dispatch + contracts)
  - Driver (deterministic device primitives)
  - Runtime (pinned dependencies)
  - Module (verified operator packages)
  - Daemon (mandatory in managed, confidential, regulated modes or when GLYPHSER_ROOT shared or world_size > 1; optional/in-process in local): Central OS service layer. Owns immutable CAS at GLYPHSER_ROOT, deterministic scheduling (job_priority + FIFO + SHA-256(CBOR_CANONICAL(["daemon_sched", [manifest_hash, hardware_attest_id, job_id]])) for reproducible allocation), launches isolated per-job process/Pod with namespace isolation (RNG/checkpoints/tapes/lineage plus persisted kernel namespace state) and explicit tensor.zero_() + sync barriers on every boundary, enforces quotas/RBAC/audits, coordinates TEE quotes and heterogeneous drivers. In local mode Bootstrap embeds equivalent in-process functionality (identical contracts, replay_token, fingerprints, certificate). Deployable as single binary or K8s operator. The daemon also registers the Tensor Memory Management Unit (TMMU) that exclusively owns and controls every tensor pointer across the job lifetime. Allocations, frees, device-to-device transfers and zeroing occur only via TMMU. Addressing is arena/offset based (injective deterministic layout) as delegated to `docs/layer2-specs/TMMU-Allocation.md` (`MapToVirtualAddresses`) and versioned there. TMMU performs static liveness analysis on UML_Model_IR (shapes known) to enable deterministic slot reuse within safety margins; enforces tensor.zero_() + synchronization barriers on every stage, job, and namespace boundary for isolation; blocks any backend direct allocation for traced tensors and contract-critical buffers. This guarantees identical virtual address plans and deterministic layout decisions within a declared hardware/driver equivalence class.
  - Management (CLI entrypoints)
  - User (manifests only)
- Filesystem roots:
  - `/datasets/<id-version-hash>/`
  - `/namespaces/<tenant_id>/<run_id>/`
  - `/jobs/queue/`
- Namespace path: `/<tenant_id>/<run_id>` where `run_id = hex(SHA-256(CBOR_CANONICAL([tenant_id, replay_token]))[0:8])` (16 hex chars).
- `GLYPHSER_ROOT` is a required immutable run-scoped root URI/path (`file://`, `s3://`, `gcs://`, or absolute local path), fixed at daemon startup.

### 0.P Bootstrap
- Single entrypoint: `Glyphser.OS.Bootstrap`
- Performs deterministic initialization, manifest/data validation, module wiring, distributed setup, and namespace entry

### 0.Q Global Manifest Additions
- `env_manifest_hash` includes `daemon_concurrency_max=16` and all required runtime fields from `docs/layer1-foundation/Environment-Manifest.md`.
- `spec_version: string`
- `tenant_id: string`
- `seed: uint64`
- `task_type`: `multiclass | binary | regression`
- `alpha` (default `1.0`)
- `execution_mode: "local" | "managed" | "confidential" | "regulated"` (default `managed`)
- `global_batch_size` (default `256`)
- `fingerprint_frequency`
- `optimizer` config
- `grad_clip_norm`
- `checkpoint_frequency`
- `job_priority` (1..10)
- `policy.rules` (optional runtime stage/action decision rules)
- `policy_bundle` (authoritative cryptographic policy commitment input; may coexist with `policy.rules`)
- `datasets: object` (keys = dataset_keys e.g. "train", "val", "test"; each value = `{id: string, version: string, hash: string}`)
- `data: {sampler_block_size?: integer (default 1048576)}`
- `custom_operators[]`
- `parallelism: {strategy: "none" | "ddp" | "fsdp" | "tensor_parallel" | "pipeline_parallel" | "hybrid", world_size_override?, sharding_config?: object}`
  - `world_size_override` semantics (normative): if provided, it MUST equal the actual initialized `world_size`; mismatch is deterministic failure (`CONTRACT_VIOLATION`).
- `manifest_inheritance: {parent_manifest_path?: string}` (resolved and merged by daemon in Bootstrap; child may override only non-security fields; security parameters inherited strictly)
- `hardware_affinity: {gpu_ids?: array of int, cpu_cores?: array of int}` (optional; daemon pins for deterministic scheduling)
- `profile: "research" | "enterprise" | "regulated"` (Bootstrap expands to execution_mode-appropriate defaults for security, quotas, evaluation metrics, pipeline_stages, and pipeline checks). If pipeline_stages absent, default is: research = [{step_id:"train",type:"train"},{step_id:"eval",type:"eval",depends_on:["train"]}], enterprise = [{step_id:"train",type:"train"},{step_id:"eval",type:"eval",depends_on:["train"]},{step_id:"infer",type:"infer",depends_on:["eval"]}], regulated = same as enterprise plus DP-forced augment stage if augment_config present.
- `backend: "pytorch" | "jax" | "custom"` (default `"pytorch"`)
- `pipeline_stages: array` of objects `{step_id: string, type: "train"|"eval"|"infer"|"augment", manifest_path?: string, depends_on?: array of step_id, dataset_key?: string}`
- `resource_requests: {cpus: int, gpus: int, memory_gb: float} (global or per-stage in pipeline_stages objects; daemon scheduler enforces)`
- `memory_arena_config: object` (optional deterministic arena configuration for TMMU initialization/planning; per-arena entries may include `capacity_bytes`, `alignment_bytes`)
- `quota: {memory_bytes_budget?: uint64, gpu_time_ms_budget?: uint64, cpu_time_ms_budget?: uint64, io_bytes_budget?: uint64}` (optional runtime enforcement thresholds consumed by kernel resource_ledger checks)
- `resource_ledger_schema` (fixed): `{flops:uint64, bytes_allocated:uint64, peak_bytes:uint64, gpu_time_ns:uint64, cpu_time_ns:uint64}`; kernel updates counters each step by summing operator-declared resource contributions (declared in operator contract metadata; this version assumes fixed per-operator costs).
- `rbac: {principals: array, permissions: map}` (optional; daemon enforces on NamespaceEnter and critical ops).
- `storage: {backend: "local" | "s3-compatible" | "gcs", endpoint?: string, bucket?: string, credentials_secret?: string}` (daemon uses for all CAS reads/writes; credentials_secret resolved securely by daemon only)
- `monitoring_export: {prometheus_endpoint?: string, log_sink?: string}` (daemon pushes deterministic metrics, audit summaries, and usage records; optional)
- `rbac_source: "local" | "ldap" | "oidc"` (default "local"; daemon integrates for `NamespaceEnter` and critical ops)
- `environment: {env_manifest_hash: bytes32, requirements_hash?: string (SHA-256 of canonical pinned dependency manifest), container_image?: string}`
- `daemon_mode: "standalone" | "cluster"` (default `"standalone"`)
- `distributed: {timeout_seconds: int (default 300)}`
- `fine_tune` config (`full` or `lora`)
- `evaluation` config
- `security: {attestation_required: bool, functional_commitment: bool (default false), differential_privacy: {enabled: bool (default false), target_epsilon: float (default 0.0)}}`
- `model` (`preset`/`preset_params`/`architecture`)
- `compute_dtype: "float32" | "float64"`
- `model.architecture` supports `type: "custom"`

Supported presets in `ExpandPreset`: `mlp_classifier`, `basic_cnn`, `resnet18`, `resnet50`, `vit_tiny`, `bert_tiny`, `gpt2_small`. LoRA insertion is deterministic from checkpoint hash.
- `fingerprint_frequency` semantics (normative): `0` disables periodic fingerprints; otherwise fingerprints run when `t % fingerprint_frequency == 0`.
- Default dataset keys per stage (if `pipeline_stages[i].dataset_key` omitted): `train -> "train"`, `eval -> "val"`, `infer -> "test"`.

### 0.R Distributed and Multi-tenancy Policy
- Deterministic rank ordering and deterministic collective primitives
- `global_batch_size % world_size == 0` required for distributed runs
- Global batch sequence is world-size invariant by data contract; update values are E0 only within fixed distributed configuration and E1 across compatible re-shards; sharding remains contiguous rank-ordered after global deterministic permutation; collective order fixed by ascending rank.
- E0 distributed requirement: all ranks MUST report identical `driver_runtime_fingerprint_hash`; mismatch is deterministic failure (or explicit downgrade to non-E0 mode if policy allows).
- Per-rank RNG derivation (normative): `rank_rng_seed = SHA-256(CBOR_CANONICAL(["rank_rng", [replay_token, uint32(rank)]]))`; each rank initializes its RNG master from this seed to avoid cross-rank stream collisions.
- In `daemon_mode=cluster`, all collectives respect manifest `distributed.timeout_seconds` (default 300); any timeout or communication error aborts deterministically with `DISTRIBUTED_COMMUNICATION_FAILURE` record (included in trace and certificate).
- Declared parallelism.strategy is implemented by the loaded driver under Contract.Validate and the ReproducibilityTest suite (sharding of model parameters and data consistent with NextBatch and UML_Model_IR node annotations). Hybrid strategies combine via manifest-defined stage or node partitioning.

### 0.S RNG Consumption Contract
- Every operator declares exact RNG draws and stream ownership
- Kernel checks declared-vs-actual offsets every call
- Violations abort with `RNG_CONSUMPTION_VIOLATION`

### 0.T Execution Model
- VI kernel procedure is the only conformant execution path

### 0.U Execution Contract
- All execution occurs exclusively through the VI kernel procedure in section 6 and registered, contract-validated operators/drivers. No user-provided training/evaluation/inference loops or direct backend calls permitted; manifest declares the complete computation graph. In managed/confidential/regulated modes, daemon and drivers sandbox execution: any non-registered library primitive call, unapproved import, or side effect triggers CONTRACT_VIOLATION abort with telemetry recorded in Contract.Validate. Custom logic permitted only via RegisterCustom operators that pass full Contract.Validate (purity, RNG consumption, ordering, determinism, IR mapping). Violations abort with CONTRACT_VIOLATION.

### 0.V Operation Modes
- `local`: daemon optional, relaxed warnings mode
- `managed`: full enforcement, signed certificate required
- `confidential`: TEE launch + quote mandatory, full enforcement, signed certificate includes quote
- `regulated`: daemon mandatory; enforces exact differential-privacy accounting, immutable append-only audit trail, and electronic signatures. Launches inside hardware TEE if present. If Security.AttestTEE fails at any point, kernel issues immediate termination, executes deterministic best-effort zeroization hooks for owned memory regions, records zeroization evidence, and aborts. Full RNG auditing; produces signed provenance record.
- Legacy framework import rule: `Glyphser.Import.LegacyFramework` is allowed only on SERVICE surface in `local`/`managed`; forbidden in `confidential`/`regulated`.

### 0.W CLI and Usability Requirements
- Required commands (prioritized entrypoints): `glyphser quickstart [template: classification|regression|pipeline|regulated]` (creates minimal ready-to-run manifest.yaml + project layout + example pipeline under current dir; runnable in <10 s), `glyphser run manifest.yaml`, `glyphser validate`, `glyphser doctor`, `glyphser replay <token>`, `glyphser certificate verify`, `glyphser migrate <legacy_path> [options] --output-dir .` (analyzes common training scripts/notebooks, generates runnable Glyphser manifest.yaml + IR; runs Contract.Validate on result), plus `job submit`/`export`/`infer`/`namespace init`/`daemon start`/`dataset register`/`import`/`audit export`/`ps/logs/kill/queue`. All CLI paths perform full Contract.Validate + manifest validation before any action.

### 0.X Training Certificate Contract
- Certificate field-set is authoritative in `docs/layer2-specs/Execution-Certificate.md` only.
- Kernel and adapters MUST NOT add implicit certificate fields outside `docs/layer2-specs/Execution-Certificate.md` `signed_payload` and allowed `unsigned_metadata`.
- Daemon signs certificate using namespace ed25519 private key; `regulated` mode additionally applies declared electronic signatures.
- `augment_metadata` for each symbolic stage (if present)

### 0.Y UML_Model_IR
Neutral declarative ML-ISA (Instruction Set Architecture) used by all Model/* system calls and drivers.
- Nodes: array of `{node_id: string, instr: string (from mandatory base set: MATMUL, CONV2D, LAYERNORM, ATTENTION, RESIDUAL_ADD, GELU, SOFTMAX, etc.), params: dict, inputs: array of node_id or 'input_data', shape_in/out: tuple(s), grad_edges?: array<node_id>}`
- `grad_edges` (optional) declares explicit gradient dependency edges for backward scheduling; when absent, reverse forward order is used subject to executor equivalence checks.
- For parallel strategies nodes include optional sharding_spec resolved by driver into device placement.
- Execution: strict topological order (stable sort by node_id on ties).
- All presets expand to valid ML-ISA. Custom layers via RegisterCustom declare full instruction mapping.
- Drivers translate ML-ISA → native executable under Contract.Validate (E0 within declared backend/hardware equivalence class; CPU reference used for E1 semantic checks).
- Canonical CBOR serialization (fixed field order) for all hashing.

### 0.Z Logging Contract (fulfills Block V.A)
`Glyphser.IO.WriteTape` serves as the canonical `LogIteration` operator. Every iteration appends a structured trace record containing all required V.B fields (`t`, `state`, `action`, `loss_total`, `grad_norm`, `state_fp`, `functional_fp`, `replay_token`/fingerprint, etc.).

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
- `theta`
- `state ∈ {S_INIT, S_TRAINING, S_EVALUATING, S_TERMINATED}`
- `t`
- `replay_token`
- `run_id`
- `current_step`
- `loss_hist`
- `data_cursors: map<string, (epoch: int, global_index: int)>` (key = dataset_key).
- `rng_master_state` + offsets
- `dp_accountant_state`, `cumulative_epsilon`
- `tmmu_context`
- `operator_contracts_root_hash`
- `resource_ledger`
- `tape_state`

### I.B Inputs and Hyperparameters
All immutable inputs and hyperparameters are declared in the YAML manifest (see `0.Q Global Manifest Additions`). Key declared items: `global_batch_size`, optimizer config, `pipeline_stages`, `security.{attestation_required, differential_privacy}`, `compute_dtype`, and related runtime policy fields.

### I.C Constraints and Feasible Set
Unconstrained optimization problem. All runtime contracts (driver determinism, purity, RNG consumption, ordering) are enforced by `Glyphser.Contract.Validate` and backend driver verification.

### I.D Transient Variables
- `batch`, `logits`, `L_tot`, `action`, `grads`, `noisy_grads`, `grad_norm`, `eval_result`, `outputs`
- Transients are iteration-local and cannot be referenced across iterations unless promoted into persistent state.

### I.E Invariants and Assertions
- Finite tensors
- Deterministic ordering
- Contract checks mandatory

### Architecture Overview (Document Wiring)
- Core execution specs: `docs/layer2-specs/Data-NextBatch.md`, `docs/layer2-specs/ModelIR-Executor.md`, `docs/layer2-specs/TMMU-Allocation.md`, `docs/layer2-specs/DifferentialPrivacy-Apply.md`.
- Interface and type contracts: `docs/layer1-foundation/API-Interfaces.md`, `docs/layer1-foundation/Data-Structures.md`, `docs/layer2-specs/Config-Schema.md`.
- Reliability and observability contracts: `docs/layer1-foundation/Error-Codes.md`, `docs/layer2-specs/Trace-Sidecar.md`, `docs/layer2-specs/Checkpoint-Schema.md`, `docs/layer2-specs/Replay-Determinism.md`.
- Delivery and compliance contracts: `docs/layer4-implementation/Backend-Adapter-Guide.md`, `docs/layer2-specs/Security-Compliance-Profile.md`, `docs/layer1-foundation/Dependency-Lock-Policy.md`, `docs/layer2-specs/Deployment-Runbook.md`.
- Planning and execution governance: `docs/layer4-implementation/Implementation-Roadmap.md`, `docs/layer4-implementation/Code-Generation-Mapping.md`, `docs/layer3-tests/Test-Plan.md`, `docs/layer3-tests/Performance-Plan.md`.
- Lifecycle and governance extensions: `docs/layer2-specs/Experiment-Tracking.md`, `docs/layer2-specs/Model-Registry.md`, `docs/layer2-specs/Monitoring-Policy.md`, `docs/layer2-specs/Evaluation-Harness.md`, `docs/layer2-specs/Data-Lineage.md`, `docs/layer2-specs/Pipeline-Orchestrator.md`, `docs/layer2-specs/Execution-Certificate.md`.
- Coding acceleration contracts: `docs/layer4-implementation/Reference-Implementations.md`, `docs/layer3-tests/Test-Vectors-Catalog.md`, `docs/layer4-implementation/Repo-Layout-and-Interfaces.md`.
- New contract subdocuments:
  - `docs/layer1-foundation/Operator-Registry-Schema.md` (authoritative registry schema),
  - `docs/layer1-foundation/Digest-Catalog.md` (digest label/value authority),
  - `docs/layer1-foundation/Canonical-CBOR-Profile.md` (single commitment serialization profile),
  - `docs/layer2-specs/Run-Commit-WAL.md` (atomic commit journal + recovery),
  - `AuthZ-Capability-Matrix.md` (operator capability policy),
  - `docs/layer1-foundation/Determinism-Profiles.md` (BITWISE/TOLERANCE runtime profiles).
- Wiring invariant: all operator names referenced across documents must be fully qualified and versioned. Shared operators may be imported by reference from dedicated contract documents (for example `Glyphser.Error.Emit` in `docs/layer1-foundation/Error-Codes.md`).

### II.F Deterministic Runtime Governance (Normative)
- Distributed reduction determinism must follow declared `determinism_profile`:
  - `BITWISE` mode requires fixed collective algorithm, fixed chunk order, fixed accumulation dtype/order, and no nondeterministic atomics.
  - `TOLERANCE` mode requires explicit per-field tolerance bands and E1 comparability policy.
- Kernel must emit deterministic policy and authorization transcripts:
  - policy transcript hash `policy_gate_hash`,
  - authorization transcript hash `authz_decision_hash`.
- End-of-run artifacts must be finalized only through the atomic run commit protocol (`trace/checkpoint/lineage/certificate` two-phase commit).

---

## 3) Initialization

1. `t <- 0`
2. `persistent_state <- Glyphser.OS.Bootstrap(manifest)`
3. `canonical_manifest <- Glyphser.Data.Manifest(manifest)` then `Glyphser.Data.ValidateManifest(canonical_manifest)`
4. `active_namespace <- Glyphser.OS.NamespaceEnter(namespace_path)`
5. `driver <- Glyphser.Backend.LoadDriver(manifest.backend)` then `dist_state <- Glyphser.Distributed.Setup(...)`
6. `arena_config <- manifest.memory_arena_config or deterministic default policy` then `tmmu_context <- Glyphser.TMMU.Init(ir_graph, "train", replay_token, arena_config)`
7. Initialize `theta` deterministically from manifest/seed contract
8. Initialize `state <- S_TRAINING`, `loss_hist`, `data_cursors`, tape, fingerprints, and RNG offsets
9. Run `Glyphser.Contract.Validate(...)` before entering the main procedure loop

---

## 4) Operator Manifest

Active operators (exact wiring table):
- `Glyphser.OS.Bootstrap`
- `Glyphser.OS.ResolvePath`
- `Glyphser.OS.NamespaceEnter`
- `Glyphser.Data.Manifest`
- `Glyphser.Data.ValidateManifest`
- `Glyphser.Data.NextBatch`
- `Glyphser.Data.RegisterDataset`
- `Glyphser.Data.ImportAndRegister`
- `Glyphser.Model.Forward`
- `Glyphser.Model.ExpandPreset`
- `Glyphser.Model.ApplyFineTune`
- `Glyphser.Objective.TotalLoss`
- `Glyphser.Optimizer.Update`
- `Glyphser.Module.RegisterCustom`
- `Glyphser.Policy.Evaluate`
- `Glyphser.Contract.Validate`
- `Glyphser.IO.WriteTape`
- `Glyphser.IO.SaveCheckpoint`
- `Glyphser.Certificate.WriteExecutionCertificate`
- `Glyphser.State.Journal`
- `Glyphser.Termination.Check`
- `Glyphser.Fingerprint.StateFingerprint`
- `Glyphser.Fingerprint.Functional`
- `Glyphser.Error.Emit`
- `Glyphser.Distributed.Setup`
- `Glyphser.Distributed.Barrier`
- `Glyphser.Evaluation.Run`
- `Glyphser.Security.AttestTEE`
- `Glyphser.Verifiable.CommitFunctional`
- `Glyphser.DifferentialPrivacy.Apply`
- `Glyphser.Backend.LoadDriver`
- `Glyphser.Pipeline.Dispatch`
- `Glyphser.Config.DeterministicStageMerge`
- `Glyphser.Inference.RunBatch`
- `Glyphser.Model.Backward`
- `Glyphser.TMMU.Init`
- `Glyphser.Symbolic.Augment`
- `Glyphser.Security.VerifyCertificate`
- `Glyphser.Certificate.EvidenceValidate`
- `Glyphser.Transition.SwitchState`
- `Glyphser.Commit.WALAppend`
- `Glyphser.Commit.FinalizeRunCommit`

---

## 5) Operator Definitions

External operator reference: `Glyphser.Error.Emit` is defined normatively in `docs/layer1-foundation/Error-Codes.md` and imported by reference.
External operator reference: `Glyphser.Commit.WALAppend` and `Glyphser.Commit.FinalizeRunCommit` are defined normatively in `docs/layer2-specs/Run-Commit-WAL.md` and imported by reference.

**Kernel System Call Interface**  
All system calls follow the EQC template and may be invoked **only** through the VI kernel procedure in section 6. No user code may call backend primitives, torch.add, jax ops, or any library function directly. Every tensor allocation, forward/backward step, or state mutation must be a syscall. Violations trigger CONTRACT_VIOLATION abort.

**Operator:** `Glyphser.OS.Bootstrap`  
**Category:** Init  
**Signature:** `(manifest -> persistent_state)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** PRNG master seeded from fixed manifest hash (single Philox + fixed offsets; no draws); parameter init; buffer allocation; data manifest load + ValidateManifest + ImportAndRegister if needed; ApplyFineTune if declared; ExpandPreset if preset set; Backend.LoadDriver(manifest.backend); Distributed.Setup; policy load; namespace enter; Security.AttestTEE (confidential mode only); resolve and merge `manifest_inheritance` if declared; apply `profile`-specific defaults and materialize default pipeline_stages if absent per 0.Q profile rule; resolve and merge manifest_inheritance before pipeline materialization; set `hardware_affinity` pinning if specified; if environment.requirements_hash declared and execution_mode != "local": compute current environment SHA-256 hash from pinned runtime manifest and abort with CONTRACT_VIOLATION on mismatch; in local mode emit deterministic warning record only (no abort). Legacy framework import is delegated to `Glyphser.Import.LegacyFramework` on SERVICE surface and forbidden in `confidential`/`regulated` modes.
**Preconditions / Postconditions:** manifest canonicalized; TEE quote valid in confidential mode.  
**Edge cases:** missing dataset hash, invalid URI, TEE unavailable.  
**Numerical considerations:** manifest-hash-derived bytes for theta init (no RNG).  
**Ordering/tie handling:** N/A.  
**Failure behavior:** `CONTRACT_VIOLATION` or `ATTESTATION_FAILURE` -> abort with record.  
**Dependencies:** 0.Q manifest fields.

**Operator:** `Glyphser.Data.Manifest`  
**Category:** Data  
**Signature:** `(manifest -> canonical_manifest)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonicalize manifest JSON/YAML; compute hash inputs.  
**Preconditions / Postconditions:** valid schema -> canonical bytes.  
**Edge cases:** malformed keys/order.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** sorted keys.  
**Failure behavior:** abort on schema mismatch.  
**Dependencies:** 0.Q schema.

**Operator:** `Glyphser.Data.ValidateManifest`  
**Category:** Data  
**Signature:** `(manifest -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates required fields, hashes, operator contracts, dataset refs.  
**Preconditions / Postconditions:** all mandatory fields present.  
**Edge cases:** missing `global_batch_size`, invalid `execution_mode`.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic field walk.  
**Failure behavior:** abort with `CONTRACT_VIOLATION`.  
**Dependencies:** 0.Q.

**Operator:** `Glyphser.Data.RegisterDataset`  
**Category:** Data  
**Signature:** `(path,id,version -> dataset_id_hash)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** computes SHA-256 over canonical dataset bytes/manifest, validates schema, stores immutable dataset under canonical path.  
**Preconditions / Postconditions:** data readable; hash persisted.  
**Edge cases:** duplicate id/version mismatch.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** lexicographic file traversal.  
**Failure behavior:** abort on hash mismatch.  
**Dependencies:** OS path resolver.

**Operator:** `Glyphser.Data.ImportAndRegister`  
**Category:** Data  
**Signature:** `(uri,id,version -> dataset_id_hash)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** imports from local/s3/hf URI then delegates to RegisterDataset.  
**Preconditions / Postconditions:** imported bytes immutable after registration.  
**Edge cases:** URI unavailable/auth failure.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic chunk/file order.  
**Failure behavior:** abort.  
**Dependencies:** RegisterDataset.

**Operator:** `Glyphser.Data.NextBatch`  
**Category:** Data  
**Signature:** `(dataset_key, world_size, rank, data_cursor_in -> batch, data_cursor_next)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic with declared RNG  
**Definition:** Uses manifest.datasets[dataset_key]. Implements memory-efficient deterministic global sampling independent of dataset size. Epoch permutation seeded by `SHA-256(CBOR_CANONICAL(["nextbatch_epoch_seed", [kernel_replay_token, manifest_hash, dataset_key, uint64(epoch)]]))` using Philox4x32-10. Partition into blocks of size manifest.data.sampler_block_size (default 1<<20). Materialize only the block permutation list (size N/B, always ≪ dataset size); within each block compute intra-block positions via the bijective mapping specified in `docs/layer2-specs/Data-NextBatch.md` (`SeededIntraBlockMap`) with explicit short-tail handling. For any global position p compute originating sample index in O(1) per sample after block list is built. Form global batches sequentially from the virtual sequence; split into contiguous rank-ordered shards. Guarantees identical global batch sequence across world_size values; update dynamics are E0 only within fixed distributed configuration and E1 across compatible re-shards. Eval and infer stages always use strict ascending original index order (no shuffle). `NextBatch` is cursor-pure; kernel persists `data_cursor_next` into `data_cursors[dataset_key]`.
**Preconditions / Postconditions:** `global_batch_size % world_size == 0`.  
**Edge cases:** world_size=1, final batch boundary.  
**Numerical considerations:** preprocessing stable in binary64 for reductions.  
**Ordering/tie handling:** ascending global index.  
**Failure behavior:** abort on invalid shard/batch.  
**Dependencies:** 0.R.

**Operator:** `Glyphser.Model.ExpandPreset`  
**Category:** Model  
**Signature:** `(model.preset, preset_params, fine_tune -> uml_model_ir_dag)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** expands known preset table into UML_Model_IR DAG; inserts LoRA adapters deterministically when configured.  
**Preconditions / Postconditions:** preset exists.  
**Edge cases:** unknown preset/target module.  
**Numerical considerations:** no RNG.  
**Ordering/tie handling:** registration order of layers.  
**Failure behavior:** abort.  
**Dependencies:** 0.Q model fields.

**Operator:** `Glyphser.Model.ApplyFineTune`  
**Category:** Model  
**Signature:** `(theta, fine_tune_cfg, uml_model_ir_dag -> theta')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** applies full or LoRA fine-tune wiring/checkpoint loading on UML_Model_IR DAG.  
**Preconditions / Postconditions:** checkpoint hash must match manifest.  
**Edge cases:** missing checkpoint, incompatible layer shapes.  
**Numerical considerations:** deterministic load/merge order.  
**Ordering/tie handling:** parameter registration order.  
**Failure behavior:** abort.  
**Dependencies:** checkpoint manifest.

**Operator:** `Glyphser.Model.Forward`  
**Category:** Model  
**Signature:** `(theta, batch, uml_model_ir_dag, replay_token, tmmu_context -> logits)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** dispatches to active backend driver; executes UML_Model_IR DAG (custom layers via registry); all reductions in binary64 with ascending-index order.  
**Preconditions / Postconditions:** architecture validated.  
**Edge cases:** empty batch, invalid custom ref.  
**Numerical considerations:** critical reductions in binary64; deterministic reduction order.  
**Ordering/tie handling:** layer order fixed by architecture list.  
**Failure behavior:** abort.  
**Dependencies:** RegisterCustom.

**Operator:** `Glyphser.Objective.TotalLoss`  
**Category:** Objective  
**Signature:** `(logits, labels, alpha, task_type -> L_tot)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** `L_sup = mean(loss_by_type)` in binary64. Multiclass: `-log(softmax(logits)[labels])` (stable log-softmax); binary: BCE with logits; regression: MSE. `L_tot = alpha * L_sup`. Reduction: exact sum then divide by batch size (ascending index).  
**Preconditions / Postconditions:** labels valid for task type.  
**Edge cases:** invalid class ids, NaN logits.  
**Numerical considerations:** stable CE/BCE/MSE paths; EPS clamps as needed.  
**Ordering/tie handling:** ascending index accumulation.  
**Failure behavior:** invalid objective policy from 0.A/0.K.  
**Dependencies:** 0.A, 0.C.

**Operator:** `Glyphser.Optimizer.Update`  
**Category:** Update  
**Signature:** `(theta, grads, optimizer_cfg -> theta')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** if optimizer==\"adamw\": `m_t = beta1*m_{t-1} + (1-beta1)*g`; `v_t = beta2*v_{t-1} + (1-beta2)*g**2`; `m_hat = m_t/(1-beta1^t)`; `v_hat = v_t/(1-beta2^t)`; `theta = theta - lr*(m_hat/(sqrt(v_hat)+eps) + weight_decay*theta)`. Optimizer moments, bias corrections, and parameter updates performed in manifest.compute_dtype; gradient norm for clipping and all scalar reductions computed in binary64 (ascending registration order); weight_decay applied after the adaptive step (standard decoupled AdamW). Other optimizers follow analogous deterministic updates in the same dtype policy.  
**Preconditions / Postconditions:** optimizer config valid.  
**Edge cases:** zero/NaN gradients.  
**Numerical considerations:** clip norm in binary64.  
**Ordering/tie handling:** parameter registration order.  
**Failure behavior:** abort on non-finite gradients.  
**Dependencies:** 0.Q optimizer.

**Operator:** `Glyphser.Module.RegisterCustom`  
**Category:** Module  
**Signature:** `(custom_operators[] -> registry')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** loads user-declared custom operators from manifest and verifies declared purity, RNG consumption, contract hash, and UML_Model_IR DAG mapping before registration.  
**Preconditions / Postconditions:** contract declaration present per operator.  
**Edge cases:** missing module path, contract mismatch.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** registration in declared manifest order.  
**Failure behavior:** abort with `CONTRACT_VIOLATION`.  
**Dependencies:** `custom_operators` manifest field.

**Operator:** `Glyphser.Policy.Evaluate`  
**Category:** Policy  
**Signature:** `(state, metrics, policy_rules -> action)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** evaluates canonical policy rules from `manifest.policy.rules` in declared order; highest priority wins; ties by lowest index. Policy-bundle hashes remain independent commitment material and are not the runtime rule source.  
**Preconditions / Postconditions:** `policy_rules` schema valid.  
**Edge cases:** no matching rule -> fallback `optimize`.  
**Numerical considerations:** comparisons in binary64.  
**Ordering/tie handling:** deterministic rule order.  
**Failure behavior:** abort on malformed rule expression.  
**Dependencies:** 0.Q.

**Operator:** `Glyphser.Evaluation.Run`  
**Category:** Evaluation  
**Signature:** `(theta, dataset_key, metrics -> eval_result)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** computes declared metrics at configured frequency; uses manifest.datasets[dataset_key]; deterministic full pass in ascending original index order (no shuffle; fixed seed=0 if any ordering needed).  
**Preconditions / Postconditions:** val split exists if configured.  
**Edge cases:** empty val split.  
**Numerical considerations:** binary64 reductions for metrics.  
**Ordering/tie handling:** ascending index over val data.  
**Failure behavior:** abort on missing eval split.  
**Dependencies:** `evaluation` manifest.

**Operator:** `Glyphser.Inference.RunBatch`  
**Category:** Inference  
**Signature:** `(theta, dataset_key, replay_token, tmmu_context -> outputs)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** uses manifest.datasets[dataset_key]; dispatches driver for inference (full pass or per-batch as configured); writes outputs and fingerprint material.  
**Preconditions / Postconditions:** backend loaded and batch schema valid.  
**Edge cases:** empty batch.  
**Numerical considerations:** binary64 for critical reductions/fingerprint path.  
**Ordering/tie handling:** ascending sample index order.  
**Failure behavior:** abort on backend/runtime mismatch.  
**Dependencies:** Backend.LoadDriver.

**Operator:** `Glyphser.Model.Backward`
**Category:** Model
**Signature:** `(L_tot, theta, ir_graph, replay_token, tmmu_context -> grads, grad_norm)`
**Purity class:** STATEFUL
**Determinism:** deterministic
**Definition:** Compute partial derivatives following ir_graph in reverse topological order. For each instruction the driver executes the corresponding gradient kernel; if the backend instruction is non-deterministic, driver falls back to binary64 CPU reference path. Global gradient norm computed with Kahan summation in binary64 (ascending index). If DP is disabled and `grad_clip_norm` is declared, apply `g = g * min(1, clip_norm / (norm + EPS_EQ))`; if DP is enabled, return unclipped gradients and perform clipping only inside `Glyphser.DifferentialPrivacy.Apply`.
**Preconditions / Postconditions:** Forward completed on same ir_graph; L_tot finite; grads returned in exact theta registration order.
**Edge cases:** single micro-batch, world_size=1.
**Numerical considerations:** Critical layers (embeddings, norms) accumulated in binary64 before cast to compute_dtype.
**Ordering/tie handling:** ascending index.
**Failure behavior:** abort on INF_GRADIENT or NAN_GRADIENT per 0.K.
**Dependencies:** loaded driver, ir_graph from Bootstrap.

**Operator:** `Glyphser.Distributed.Setup`  
**Category:** Distributed  
**Signature:** `(parallelism, world_size, backend -> dist_state)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** initializes deterministic collectives and rank order; validates identical distributed determinism profile across ranks and derives per-rank RNG masters using `rank_rng_seed` rule from 0.R.  
**Preconditions / Postconditions:** valid backend and world size.  
**Edge cases:** world_size=1.  
**Numerical considerations:** deterministic reduction primitives only.  
**Ordering/tie handling:** ascending rank.  
**Failure behavior:** abort on unsupported backend.  
**Dependencies:** 0.R.

**Operator:** `Glyphser.Distributed.Barrier`
**Category:** Distributed
**Signature:** `(() -> ok)`
**Purity class:** STATEFUL
**Determinism:** deterministic
**Definition:** executes a deterministic global barrier across ranks using ascending-rank coordination and timeout `manifest.distributed.timeout_seconds`.
**Failure behavior:** abort on timeout/communication failure with deterministic code `DISTRIBUTED_COMMUNICATION_FAILURE`.
**Dependencies:** distributed communicator state.

**Operator:** `Glyphser.Backend.LoadDriver`  
**Category:** Backend  
**Signature:** `(manifest.backend -> driver_handle)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** Loads and verifies backend driver contract (including binary/manifest hash check against any regulated-mode registry); binds dispatch table for Forward/Update/Distributed/Backward; runs minimal ReproducibilityTest subset on load (E0 on tiny graphs); aborts with `BACKEND_CONTRACT_VIOLATION` on failure.  
**Preconditions / Postconditions:** driver implements all required primitives.  
**Edge cases:** unknown backend id.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** abort `BACKEND_CONTRACT_VIOLATION`.  
**Dependencies:** manifest `backend`.

**Operator:** `Glyphser.TMMU.Init`
**Category:** Memory
**Signature:** `(ir_dag, mode, replay_token, arena_config -> tmmu_context)`
**Purity class:** STATEFUL
**Determinism:** deterministic
**Definition:** initializes deterministic TMMU run context from IR + mode + replay token, validates arena capacities/alignments, and creates memory handles used by model executor operators.
**Preconditions / Postconditions:** backend loaded; `arena_config` resolved from manifest/default policy.
**Failure behavior:** abort on invalid arena config or TMMU init failure.
**Dependencies:** `docs/layer2-specs/TMMU-Allocation.md`.

**Operator:** `Glyphser.Pipeline.Dispatch`  
**Category:** Pipeline  
**Signature:** `(pipeline_stages, current_step -> next_manifest, action)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Resolves dependency graph; returns next stage manifest or termination.  
**Preconditions / Postconditions:** stage ids unique and resolvable.  
**Edge cases:** missing dependency.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic topological order with stable tie-break.  
**Failure behavior:** abort on cycle or missing dependency.  
**Dependencies:** manifest `pipeline_stages`.

**Operator:** `Glyphser.Config.DeterministicStageMerge`
**Category:** Config
**Signature:** `(base_manifest, stage_manifest -> merged_manifest)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** canonical base-first merge where stage manifest may override only non-security fields (`pipeline stage-local hyperparameters`, `dataset_key`, `checkpoint flags`, `evaluation options`). Security/policy identity fields (`policy_bundle_hash`, security mode, attestation requirements, authz/monitor/dp/redaction policy hashes, tenant identity) MUST remain unchanged. Output is re-validated by `Glyphser.Data.ValidateManifest`.

**Operator:** `Glyphser.Contract.Validate`  
**Category:** Contract  
**Signature:** `(runtime_state -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks declared invariants, objective finiteness, RNG delta contracts, ordering contracts; additionally verifies backend driver contract and pipeline DAG acyclicity.  
**Preconditions / Postconditions:** all required telemetry present.  
**Edge cases:** local relaxed mode emits warnings.  
**Numerical considerations:** EPS_EQ thresholding.  
**Ordering/tie handling:** deterministic check order.  
**Failure behavior:** abort/warn per execution mode.  
**Dependencies:** 0.V.

**Operator:** `Glyphser.Fingerprint.StateFingerprint`  
**Category:** Fingerprint  
**Signature:** `(state -> state_fp)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** incremental SHA-256 chaining over deterministic state tuples (domain-separated canonical CBOR).  
**Preconditions / Postconditions:** persistent state serializable.  
**Edge cases:** empty history.  
**Numerical considerations:** binary64 serialization for critical tensors/metrics.  
**Ordering/tie handling:** deterministic serialization order.  
**Failure behavior:** abort on serialization mismatch.  
**Dependencies:** persistent state schema.

**Operator:** `Glyphser.Fingerprint.Functional`  
**Category:** Fingerprint  
**Signature:** `(theta, probe_set -> functional_fp)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** runs canonical probe set (first 1024 items deterministic), computes probe loss/metric, hashes bytes into functional fingerprint.  
**Preconditions / Postconditions:** probe set available.  
**Edge cases:** dataset size < 1024 uses cyclic repeat.  
**Numerical considerations:** binary64 path.  
**Ordering/tie handling:** ascending original index.  
**Failure behavior:** abort on non-finite probe outputs.  
**Dependencies:** dataset manifest.

**Operator:** `Glyphser.Verifiable.CommitFunctional`  
**Category:** Fingerprint  
**Signature:** `(probe_outputs_bytes, functional_fp, security.functional_commitment -> commitment?)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** if enabled, compute `functional_commitment = SHA-256(CBOR_CANONICAL(["functional_commitment", [probe_outputs_bytes, functional_fp]]))` and attach to trace/certificate. `probe_outputs_bytes` is canonical CBOR serialization of probe outputs in deterministic probe order.
**Preconditions / Postconditions:** functional_fp available.  
**Edge cases:** disabled path returns no commitment.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** canonical byte order.  
**Failure behavior:** abort on digest mismatch.  
**Dependencies:** `security.functional_commitment`.

**Operator:** `Glyphser.Certificate.EvidenceValidate`
**Category:** Security
**Signature:** `(manifest, trace, checkpoint, replay_context -> valid: bool, report: dict)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** validates pre-sign evidence coherence and consistency (`manifest_hash`, `trace_final_hash`, `checkpoint_hash`, `lineage_root_hash`, `policy_bundle_hash`, `replay_token`, and related run-bound commitments) before certificate signing.

**Operator:** `Glyphser.Security.VerifyCertificate`
**Category:** Security
**Signature:** `(certificate_input_or_path, trust_roots? -> valid: bool, report: dict)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Accepts canonical certificate object/bytes or path as `certificate_input_or_path`; if path is provided, deterministic loading is part of this operator. Verifies daemon/HSM/electronic signatures, Merkle trace root, all pipeline lineage hashes, state_fp/functional_fp consistency (within EPS_EQ where applicable), privacy budget <= target (if present), and attestation quote (if confidential/regulated). Returns structured report with per-section pass/fail.
**Preconditions / Postconditions:** certificate readable and schema-valid.
**Edge cases:** missing quote, signature mismatch, token mismatch.
**Numerical considerations:** binary64 EPS_EQ for fingerprint checks.
**Ordering/tie handling:** N/A.
**Failure behavior:** returns false + detailed report (non-abort).
**Dependencies:** 0.X.

**Operator:** `Glyphser.Security.AttestTEE`  
**Category:** Security  
**Signature:** `(execution_mode, manifest_hash, replay_token -> quote)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic protocol path  
**Definition:** in confidential mode, collect hardware quote covering kernel measurement + manifest hash + replay token; store for certificate.  
**Preconditions / Postconditions:** TEE available and quote valid.  
**Edge cases:** unavailable TEE, invalid quote, mismatch measurement.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** `ATTESTATION_FAILURE` abort.  
**Dependencies:** confidential execution mode.

**Operator:** `Glyphser.IO.WriteTape`  
**Category:** IO  
**Signature:** `(event -> tape_state')`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** append event in deterministic order with fixed block/chaining rules.  
**Preconditions / Postconditions:** tape open and writable.  
**Edge cases:** block rollover.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** ascending t.  
**Failure behavior:** abort on write/hash mismatch.  
**Dependencies:** tape state.

**Operator:** `Glyphser.State.Journal`
**Category:** IO
**Signature:** `(t, stage_id, data_cursors, rng_offsets, resource_ledger, dp_accountant_state?, state_fp? -> journal_state')`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Write-ahead log: append cryptographically chained record (`SHA-256(CBOR_CANONICAL(["journal_link", [previous_hash, event, uint64(t)]]))`) to journal before any state mutation is visible.
Journal operator computes deterministic hashes internally:
  - `data_cursors_hash = ObjectDigest(data_cursors)` where `ObjectDigest(x) = SHA-256(CBOR_CANONICAL(x))`
  - `rng_offsets_hash = ObjectDigest(rng_offsets)`
  - `resource_ledger_hash = ObjectDigest(resource_ledger)`
  - `dp_accountant_state_hash = ObjectDigest(dp_accountant_state)` when present.
Canonical journal event shape (normative): CBOR map containing
`{t:uint64, stage_id:string, data_cursors_hash:bytes32, rng_offsets_hash:bytes32, resource_ledger_hash:bytes32, dp_accountant_state_hash?:bytes32, state_fp?:bytes32}`.
Storage location (normative): append-only per-run file under namespace journal path (e.g., `<namespace>/journal/run_journal.cborlog`); concrete filesystem target is resolved via `Glyphser.OS.ResolvePath`.
Scope clarification: Journal records incremental step-state transitions for recovery/audit and is distinct from commit WAL (`Glyphser.Commit.WALAppend`), which is only the atomic artifact-finalization protocol.
**Preconditions / Postconditions:** journal open; hash chain preserved.
**Failure behavior:** abort on write failure.

**Operator:** `Glyphser.IO.SaveCheckpoint`  
**Category:** IO  
**Signature:** `(state -> checkpoint)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** writes full checkpoint at frequency or termination using deterministic serialization. In distributed mode, rank 0 writes the canonical checkpoint after deterministic gather/barrier; checkpoint payload must include `theta`, `data_cursors`, `rng_master_state`/offsets, and `dp_accountant_state` when DP is enabled, plus sharding metadata needed for restore.
**Preconditions / Postconditions:** checkpoint path resolved in namespace.  
**Edge cases:** checkpoint_frequency=0 disables periodic writes.  
**Numerical considerations:** binary64 for critical values.  
**Ordering/tie handling:** fixed field order.  
**Failure behavior:** abort on write/serialize failure.  
**Dependencies:** section 10 schema.

**Operator:** `Glyphser.Certificate.WriteExecutionCertificate`  
**Category:** IO  
**Signature:** `(run_state -> execution_certificate.cbor)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** emits canonical `ExecutionCertificate` object exactly as defined in `docs/layer2-specs/Execution-Certificate.md`. Legacy `Glyphser.IO.WriteTrainingCertificate` is deprecated and must be implemented as a thin alias wrapper to this operator.
**Preconditions / Postconditions:** daemon signing key available.  
**Edge cases:** missing quote in confidential mode.  
**Numerical considerations:** deterministic digest encoding.  
**Ordering/tie handling:** ascending t in trace chain.  
**Failure behavior:** abort on signing failure.  
**Dependencies:** daemon key + 0.X contract.

**Operator:** `Glyphser.Termination.Check`  
**Category:** Termination  
**Signature:** `(state, limits -> bool)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** evaluates manifest termination criteria.  
`limits` schema (normative): `{max_steps_per_stage?:uint64, max_epochs?:uint64, max_wall_time_seconds?:uint64}`; check order is fixed by key order above.
Wall-time reproducibility note (normative): if `max_wall_time_seconds` is used, E0/E1 reproducibility is not guaranteed due to runtime timing variance; such runs are comparable only under looser replay equivalence policies.
**Preconditions / Postconditions:** criteria declared.  
**Edge cases:** max_steps=0.  
**Numerical considerations:** EPS_EQ comparisons.  
**Ordering/tie handling:** deterministic criterion order.  
**Failure behavior:** abort on invalid criteria.  
**Dependencies:** manifest limits.

**Operator:** `Glyphser.Transition.SwitchState`  
**Category:** Transition  
**Signature:** `(state, action -> state')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** transitions among declared lifecycle states for evaluate/train/terminate paths.  
State transition table (normative):
- `S_INIT + train -> S_TRAINING`
- `S_TRAINING + optimize -> S_TRAINING`
- `S_TRAINING + eval -> S_EVALUATING`
- `S_EVALUATING + optimize -> S_TRAINING`
- `S_TRAINING|S_EVALUATING|S_INFERENCING + infer -> S_INFERENCING`
- `ANY + terminate -> S_TERMINATED`
- other transitions are invalid and abort with `CONTRACT_VIOLATION`.
**Preconditions / Postconditions:** valid action-state pair.  
**Edge cases:** invalid transition.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** abort on invalid transition.  
**Dependencies:** state model.

**Operator:** `Glyphser.OS.ResolvePath`  
**Category:** OS  
**Signature:** `(logical_path, namespace -> absolute_path)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** resolves canonical namespace-bound path under `GLYPHSER_ROOT`.  
**Preconditions / Postconditions:** namespace exists and caller authorized.  
**Edge cases:** invalid traversal (`..`) or missing namespace path.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** lexicographic canonicalization.  
**Failure behavior:** abort.  
**Dependencies:** daemon ACL/namespace state.

**Operator:** `Glyphser.OS.NamespaceEnter`  
**Category:** OS  
**Signature:** `(namespace_path -> active_namespace)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** resolves `namespace_path` via `Glyphser.OS.ResolvePath` then enters namespace and binds filesystem, RNG, and state scopes.  
**Preconditions / Postconditions:** ACL allows access.  
**Edge cases:** non-existent namespace.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** abort.  
**Dependencies:** daemon namespace registry.


**Operator:** `Glyphser.DifferentialPrivacy.Apply`  
**Category:** Security  
**Signature:** `(microbatch_gradients_seq, security.differential_privacy, t -> noisy_gradients, updated_budget)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** If enabled (forced true in regulated mode), consumes deterministic per-step micro-batch gradient sequence, clips per-sample/per-micro-batch gradients to configured norms in binary64, averages in ascending deterministic micro-batch/index order, then adds isotropic Gaussian noise ~ N(0, σ²) using deterministic moments accountant (δ=1e-5 fixed, exact composition per standard reference implementation). RNG for noise drawn from declared stream. Cumulative privacy loss tracked exactly in binary64. Aborts with PRIVACY_BUDGET_EXCEEDED if cumulative ε exceeds target_epsilon. Noise applied to averaged gradients before Update.
**Preconditions / Postconditions:** called only on raw gradients before any optimizer step; `target_epsilon` declared and remaining budget sufficient.  
**Edge cases:** epsilon=0, zero gradients.  
**Numerical considerations:** noise scale computed exactly in binary64.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** abort with `PRIVACY_BUDGET_EXCEEDED`.  
**Dependencies:** regulated mode, 0.Q security fields.

**Operator:** `Glyphser.Symbolic.Augment`
**Category:** Symbolic
**Signature:** `(theta_snapshot, dataset_subset, augment_config -> theta', augment_metadata)`
**Purity class:** STATEFUL
**Determinism:** deterministic (with declared RNG consumption)
**Definition:** Applies sequence of deterministic non-learning transforms declared in augment_config (array of objects `{transform_type: "prune_magnitude" | "quantize_int8" | "sparsify" | "custom", params: dict}`). Operates on frozen theta_snapshot using subset from dataset_key. All operations deterministic (no RNG unless explicitly declared in custom); critical reductions in binary64. Returns theta' and augment_metadata (applied transforms list, activation statistics hashes).
**Preconditions / Postconditions:** stage type "augment"; previous stage completed; `augment_config` declared in stage manifest.
**Edge cases:** empty subset, no rules declared.
**Numerical considerations:** deterministic reductions and ordering in binary64.
**Ordering/tie handling:** rule application order from manifest.
**Failure behavior:** abort per 0.K on contract violation.
**Dependencies:** stage type "augment", manifest `augment_config`.


---

## 6) Procedure

```text
1. Glyphser.OS.Bootstrap(...)
1a. run_id <- hex(SHA-256(CBOR_CANONICAL([manifest.tenant_id, replay_token]))[0:8])  # deterministic 16-char hex run id
1b. namespace_path <- "/" + manifest.tenant_id + "/" + run_id
1c. operator_contracts_root_hash <- manifest.operator_contracts_root_hash
2. Glyphser.OS.NamespaceEnter(namespace_path)
3. Glyphser.Backend.LoadDriver(manifest.backend)
3a. arena_config <- (manifest.memory_arena_config is defined) ? manifest.memory_arena_config : derive_default_arena_config(manifest.hardware_affinity, manifest.backend)
3b. tmmu_context <- Glyphser.TMMU.Init(ir_graph, "train", replay_token, arena_config)
4. WALRecover(manifest.tenant_id, run_id)  // deterministic crash recovery before new run prepare
5. current_step <- 0
6. checkpoint_frequency <- manifest.checkpoint_frequency or 0
7. current_stage <- Glyphser.Pipeline.Dispatch(manifest.pipeline_stages, current_step)  // resolves initial stage
7a. if current_stage.manifest_path exists: stage_manifest <- Glyphser.Data.Manifest(current_stage.manifest_path); Glyphser.Data.ValidateManifest(stage_manifest); manifest <- Glyphser.Config.DeterministicStageMerge(manifest, stage_manifest)
8. wal_prepare_record <- {record_type: "PREPARE"}
8a. WALAppend(manifest.tenant_id, run_id, wal_prepare_record)
9. state <- Glyphser.Transition.SwitchState(S_INIT, current_stage.type)

Loop until Pipeline.Dispatch returns termination:
- terminated <- Glyphser.Termination.Check(...) (scoped to current stage)
- terminated <- terminated OR check_global_termination_limits(manifest, t, state)
- if terminated: break
- if t == UINT64_MAX: Error.Emit(COUNTER_OVERFLOW, ...); Glyphser.IO.WriteTape(error_record_sync); abort
- t <- t + 1
- Glyphser.Contract.Validate(...)
- if current_stage.type == "augment":
  state <- Glyphser.Transition.SwitchState(state, "train")
  theta, augment_metadata <- Glyphser.Symbolic.Augment(...)
- else:
  dataset_key <- current_stage.dataset_key or default-per-type
  if current_stage.type == "train":
    state <- Glyphser.Transition.SwitchState(state, "train")
    batch, cursor_next <- Glyphser.Data.NextBatch(dataset_key, world_size, rank, current_stage.type, data_cursors[dataset_key])
    data_cursors[dataset_key] <- cursor_next
    if len(batch) == 0:
      Glyphser.IO.WriteTape({t, stage_id: current_stage.step_id, status:"batch_empty", dataset_key})
      continue
    logits <- Glyphser.Model.Forward(theta, batch, ir_graph, replay_token, tmmu_context)
    L_tot <- Glyphser.Objective.TotalLoss(...)
    action <- Glyphser.Policy.Evaluate(...)
    if action == "optimize":
      update_grads <- null
      if manifest.security.differential_privacy.enabled == true:
          # split batch deterministically into contiguous micro-batches of size max_microbatch in original sample order (last chunk may be smaller)
          # DP-enabled path: micro-batch accumulation/noise/accounting are handled inside Apply; manifest.gradient_accumulation_steps is not used directly by this loop.
          micro_seq <- deterministic_split(batch, manifest.security.differential_privacy.max_microbatch)
          micro_grads_seq <- []
          for each micro_batch in micro_seq (deterministic order):
              micro_logits <- Glyphser.Model.Forward(theta, micro_batch, ir_graph, replay_token, tmmu_context)
              micro_loss <- Glyphser.Objective.TotalLoss(...)
              micro_grads, _ <- Glyphser.Model.Backward(micro_loss, theta, ir_graph, replay_token, tmmu_context)  # raw micro-batch gradients
              micro_grads_seq.append(micro_grads)
          noisy_grads, budget <- Glyphser.DifferentialPrivacy.Apply(micro_grads_seq, manifest.security.differential_privacy, t)
          update_grads <- noisy_grads
          cumulative_epsilon <- budget.epsilon
          dp_accountant_state <- budget.accountant_state
      else:
          grads, grad_norm <- Glyphser.Model.Backward(L_tot, theta, ir_graph, replay_token, tmmu_context)
          update_grads <- grads
      theta <- Glyphser.Optimizer.Update(update_grads, ...)
    else if action == "eval" or current_stage.type == "eval":
      state <- Glyphser.Transition.SwitchState(state, "eval")
      Glyphser.Evaluation.Run(theta, dataset_key, ...)
    else if action == "infer":
      state <- Glyphser.Transition.SwitchState(state, "infer")
      Glyphser.Inference.RunBatch(theta, dataset_key, replay_token, tmmu_context)
  else if current_stage.type == "eval":
    state <- Glyphser.Transition.SwitchState(state, "eval")
    Glyphser.Evaluation.Run(theta, dataset_key, ...)
  else if current_stage.type == "infer":
    state <- Glyphser.Transition.SwitchState(state, "infer")
    Glyphser.Inference.RunBatch(theta, dataset_key, replay_token, tmmu_context)
- checkpoint_due <- (checkpoint_frequency > 0 and (t % checkpoint_frequency == 0)) or current_stage.checkpoint_on_exit == true
- if checkpoint_due:
    if world_size == 1 or rank == 0: Glyphser.IO.SaveCheckpoint(...)
    if world_size > 1: Glyphser.Distributed.Barrier()
- if manifest.fingerprint_frequency > 0 and (t % manifest.fingerprint_frequency == 0): StateFingerprint, Fingerprint.Functional(theta, manifest.evaluation.probe_set), Verifiable.CommitFunctional (if enabled)
- Glyphser.IO.WriteTape(...) (includes stage transition and usage record)
- resource_ledger <- update deterministic per-step resource counters `{flops, bytes_allocated, peak_bytes, gpu_time_ns, cpu_time_ns}` by summing declared per-operator contributions for operators executed in this step (operator resource contributions are defined in operator contract metadata; this version assumes fixed per-operator costs).
  # quota policy schema/semantics are governed by `docs/layer2-specs/Pipeline-Orchestrator.md` (`QuotaPolicy`)
- if resource_ledger exceeds manifest quota policy:
    Error.Emit(CONTRACT_VIOLATION, ...)
    Glyphser.IO.WriteTape(error_record_sync)
    abort
- Glyphser.State.Journal(t, current_stage.step_id, data_cursors, rng_offsets, resource_ledger, dp_accountant_state?, state_fp?)
- current_step <- current_step + 1
- current_stage = Glyphser.Pipeline.Dispatch(manifest.pipeline_stages, current_step)  // advance or terminate
- if current_stage.manifest_path exists: stage_manifest <- Glyphser.Data.Manifest(current_stage.manifest_path); Glyphser.Data.ValidateManifest(stage_manifest); manifest <- Glyphser.Config.DeterministicStageMerge(manifest, stage_manifest)

On full termination:
- state <- Glyphser.Transition.SwitchState(state, "terminate")
- Glyphser.Certificate.EvidenceValidate(manifest, trace, checkpoint, replay_context)  // verify assembled evidence bundle before signing
- execution_certificate <- Glyphser.Certificate.WriteExecutionCertificate(...)
- certificate_hash <- SHA-256(CBOR_CANONICAL(execution_certificate))
- wal_cert_signed_record <- {record_type: "CERT_SIGNED", certificate_tmp_hash: certificate_hash}
- WALAppend(manifest.tenant_id, run_id, wal_cert_signed_record)
- FinalizeRunCommit(manifest.tenant_id, run_id)
- operator_registry_hash <- operator_contracts_root_hash  # same commitment in this contract suite
- wal_finalize_record <- {
    record_type: "FINALIZE",
    trace_final_hash,
    checkpoint_hash,
    lineage_root_hash,
    certificate_hash,
    manifest_hash,
    policy_bundle_hash,
    operator_registry_hash,
    determinism_profile_hash
  }
- WALAppend(manifest.tenant_id, run_id, wal_finalize_record)
- Glyphser.Security.VerifyCertificate(output_certificate_path)  // post-write self-verification of produced certificate
```

---

## 7) Trace & Metrics

### Logging rule
Each iteration must emit one canonical trace record via `Glyphser.IO.WriteTape` with required V.B fields for the active task type.
- `operator_seq` is initialized to `0` at the beginning of each step and incremented for each operator call in procedure order.

### Trace schema (minimum required)
- `run_header`: metadata, hashes, replay_token, task_type, world_size, backend_binary_hash, driver_runtime_fingerprint_hash
- `iter`: `t, stage_id, operator_id, operator_seq, rank, status, loss_total?, grad_norm?, state_fp?, functional_fp?, rng_offset_before?, rng_offset_after?, state?, action?`
- `run_end`: status, final hashes, final fingerprints

### Metric schema
- `loss_total`, `grad_norm`, `functional_fp`, `cumulative_epsilon` (regulated mode)

### Comparability guarantee
Two implementations/runs are comparable if they share identical trace schema, metric schema, replay_token definition, objective preorder, and constraint policy (E0 for bitwise, E1 for metric).
- `state`/`action` are mandatory only for RL task types; optional otherwise.

### Certificate schema
- Signed `training_certificate.cbor` with Merkle root, lineage, fingerprints, manifest/contract hashes, and confidential quote when applicable

---

## 8) Validation
#### VII.A Lint rules (mandatory)
Spec passes: symbol completeness, no hidden globals, total state updates per iteration, stochastic explicitness (RNG only inside operators), edge-case totality, ordering/tie adherence, trace compliance, manifest completeness, purity class for all operators, failure semantics traceable, data provenance declared, global batch independence.
- pipeline DAG acyclic and all stages reference valid manifests; backend driver contracts satisfied.

#### VII.B Operator test vectors (mandatory)
Every operator has deterministic test vectors (input → output within EPS_EQ) and stochastic replay-token verification (seed → exact sequence).

#### VII.C Golden traces (mandatory)
At least one golden run trace per execution_mode for reference seed + any manifest-declared dataset. Regression criteria: exact replay_token, state_fp sequence, functional_fp curve within declared tolerance envelope over 10 seeds (E1).

---

## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- **E0 Trace-equivalent** (bitwise identical trace and certificate)
- **E1 Metric-equivalent** (identical loss/functional_fp curves within tolerance)
- **E2 Distribution-equivalent** (statistical replay over seeds)
- **E3 Invariant-equivalent** (same contracts and state_fp sequence)

Required level for any change: E1 minimum; E0 for kernel, attestation, or RNG contract changes.

#### VIII.B Allowed refactor categories
- algebraic simplification of loss or fingerprint
- numerical stabilization (clamps, ordering)
- vectorization/batching (preserve reduction order)
- parallelization (re-declare 0.R sharding)
- operator replacement via version bump + manifest update
- driver certification (new hardware TEE backend)
- declarative-only entrypoint preservation, kernel-only execution, manifest-driven dispatch, dataset registration immutability, signed certificate portability
- regulated-mode additions (differential-privacy accounting, compliance report generation, electronic signatures)

Breaking observables require trace schema update + MAJOR version bump.

#### VIII.C Equivalence test procedure (mandatory)
- 10 seeds per golden dataset
- metrics: replay_token, state_fp sequence, functional_fp curve, final theta (binary64)
- thresholds: EPS_EQ for scalars, exact Merkle root for certificate
- statistical test for E2: Kolmogorov-Smirnov on loss curves (α=0.01, Bonferroni-corrected).
- regulated-mode artefacts: exact cumulative epsilon, signed compliance report, electronic signature validation.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- canonicalized full manifest (including pipeline_stages)
- operator contract hashes
- `theta`, optimizer state
- `loss_hist`, `data_cursors`
- RNG master state + offsets
- `policy_bundle_hash`, `env_manifest_hash`, `replay_token`, `backend_binary_hash`, `driver_runtime_fingerprint_hash`
- latest `state_fp`, `functional_fp`, optional `functional_commitment`
- pipeline lineage state

### Serialization
- deterministic canonical CBOR encoding with fixed field order

### Restore semantics
- restore produces identical subsequent control flow under same manifest/seed/replay token contract
- in confidential mode, attestation must be re-validated before resuming

### Post-termination export
- `theta.pt`
- `inference_manifest.yaml`
- `training_certificate.cbor`
- `model.onnx`
- `model_card.json`

---
## 11) Sealed Execution and Extension Governance (Normative)
- Sealed execution mode:
  - user-provided training/eval loops are forbidden,
  - execution proceeds only via manifest-driven registered operators.
- Extension points:
  - custom behavior allowed only via declared `RegisterCustom` style registry pathways with digest-pinned contracts.
- Governance rule:
  - any extension must preserve deterministic trace/certificate semantics and pass conformance gating for the active profile.
