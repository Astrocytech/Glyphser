# Glyphser Data Lineage Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Data.Lineage`  
**Purpose (1 sentence):** Define deterministic dataset snapshot lineage and transform-chain provenance for replayable training/evaluation runs.  
**Spec Version:** `Glyphser.Data.Lineage` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Data provenance and versioning.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Data.Lineage`
- **Purpose (1 sentence):** Deterministic dataset snapshot provenance.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize unverifiable data lineage.
### 0.B Reproducibility Contract
- Replayable given `(dataset_snapshot_id, data_access_plan_hash, transform_chain_hash)`.
### 0.C Numeric Policy
- Hashes/IDs exact.
### 0.D Ordering and Tie-Break Policy
- Transform chain ordering fixed by declared transform_seq.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-source merges resolved deterministically by sorted source ID.
### 0.F Environment and Dependency Policy
- Data import and transforms must be content-addressed and immutable.
### 0.G Operator Manifest
- `Glyphser.Data.BuildSnapshot`
- `Glyphser.Data.ComputeLineageHash`
- `Glyphser.Data.ValidateSnapshot`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Data.*` namespace.
### 0.I Outputs and Metric Schema
- Outputs: `(dataset_snapshot_id, data_access_plan_hash, lineage_report)`
- Metrics: `source_count`, `transform_count`, `snapshot_size_bytes`
### 0.J Spec Lifecycle Governance
- snapshot ID and lineage hash semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- abort on snapshot hash mismatch or missing lineage refs.
### 0.L Input/Data Provenance
- lineage includes source hashes and transform chain hash.

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
- snapshot catalog and lineage graph.
### I.B Inputs and Hyperparameters
- `tenant_id`, `run_id`, source refs, split configs, transform specs, `sampler_config_hash`.
### I.C Constraints and Feasible Set
- snapshot immutable after publish.
### I.D Transient Variables
- hashing buffers and lineage diagnostics.
### I.E Invariants and Assertions
- every snapshot ID is content-addressed and deterministic.

### II.F Snapshot Identifier (Normative)
- Stable content identity:
  - `dataset_root_hash` is computed over dataset files as:
    - enumerate files under dataset root with normalized POSIX-style relative paths (forward slashes, no `.`/`..`, no repeated separators, no leading slash) sorted lexicographically,
    - `file_hash_i = SHA-256(file_bytes_i)`,
    - `leaf_i = SHA-256(CBOR_CANONICAL(["dataset_leaf", [relative_path_i, file_hash_i]]))`,
    - Merkle parent `node = SHA-256(CBOR_CANONICAL(["dataset_node", [left, right]]))` with odd-leaf duplication,
    - root is `dataset_root_hash`.
  - `split_hashes = SHA-256(CBOR_CANONICAL(["split_defs", split_defs_sorted]))` where `split_defs_sorted` is split config sorted by split name.
  - split-name uniqueness rule: `split_name` values MUST be unique within `split_defs`; duplicates are deterministic validation failure.
  - split derivation algorithm (normative):
    - start from dataset canonical deterministic order:
      - for multi-file datasets, file order is normalized POSIX relative path order (lexicographic ascending),
      - within each file, record order is the physical storage order of that file format (for example line order for text files, native record order for binary containers),
    - if `split_seed` is present, apply deterministic seeded permutation before assignment:
      - for each sample at canonical position `sample_index`, compute
        `shuffle_key = SHA-256(CBOR_CANONICAL([split_seed, sample_index]))`,
      - sort samples lexicographically by `shuffle_key` (tie-break by `sample_index`),
      - use that sorted order as the shuffled dataset order,
    - assign sequential ranges by split fractions in split order:
      - for each split except the last, `split_count_i = floor(split_fraction_i * total_samples)`,
      - any remaining samples after these assignments are assigned to the final split.
    - after computing split counts, validation rule: split fractions must satisfy `abs(sum(split_fraction_i) - 1.0) <= EPS_EQ`; otherwise deterministic validation failure.
  - canonical split entry encoding: `{"split_name":string,"split_fraction":float64,"split_seed?:uint64}` encoded as canonical CBOR map.
  - `dataset_snapshot_id = SHA-256(CBOR_CANONICAL([tenant_id, [dataset_root_hash, split_hashes, transform_chain_hash, dataset_version_or_tag]]))`
- Run/access-plan identity:
  - `world_size_policy = "rank_contiguous_shard"` (must match `docs/layer2-specs/Data-NextBatch.md`).
  - `epoch_seed_rule = "epoch_seed_rule"` (must match `docs/layer2-specs/Data-NextBatch.md`).
  - `data_access_plan_hash = SHA-256(CBOR_CANONICAL([kernel_replay_token, [manifest_hash, dataset_key, sampler_config_hash, world_size_policy, epoch_seed_rule]]))`
- `dataset_snapshot_id` and `data_access_plan_hash` are distinct and MUST NOT be conflated.
- Both `dataset_snapshot_id` and `data_access_plan_hash` MUST be emitted in trace and bound in execution certificate payload.
- Cross-tenant rule: all lineage objects are namespaced by `(tenant_id, object_id)`; cross-tenant references must hard-fail deterministically.
- CAS retention metadata is mandatory:
  - `retention_class ∈ {golden, certified_release, experimental, ephemeral}`,
  - `pin_root_refs` (certificate/model-release roots),
  - `gc_eligible_after_utc`.
- GC invariant: lineage objects reachable from active certificate/release roots are not collectible.
- default retention rule: if unspecified, `retention_class = experimental`.
- Commit binding: finalized lineage objects must participate in the atomic run commit protocol and be referenced by `lineage_root_hash` in the execution certificate.

### II.G Lineage Commitments (Normative)
- `transform_chain_hash = SHA-256(CBOR_CANONICAL(["transform_chain", transforms_sorted_by_seq]))`.
- Transform ordering rule: each transform entry MUST include `seq:uint64`; `transforms_sorted_by_seq` sorts ascending by `seq` (ties are deterministic failure).
- `object_type` domain (normative): one of `{ "dataset", "transform", "split", "artifact", "policy", "checkpoint" }`.
- `object_id` domain (normative): content-addressed identifier of the lineage object payload in its namespace.
- `lineage_object_hash = SHA-256(CBOR_CANONICAL(["lineage_object", [object_type, object_id, payload]]))`.
  - `payload` is the canonical CBOR serialization of the lineage object's committed content.
- `lineage_root_hash` uses deterministic Merkle construction:
  - leaf list: sorted by `(object_type, object_id)` ascending,
  - leaf hash: `leaf_i = SHA-256(CBOR_CANONICAL(["lineage_leaf", [object_type_i, object_id_i, lineage_object_hash_i]]))`,
  - parent hash: `node = SHA-256(CBOR_CANONICAL(["lineage_node", [left, right]]))`,
  - odd-leaf rule: duplicate last leaf.

---
## 3) Initialization
1. Load source references.
2. Validate transform chain.
3. Initialize snapshot build context.

---
## 4) Operator Manifest
- `Glyphser.Data.BuildSnapshot`
- `Glyphser.Data.ComputeLineageHash`
- `Glyphser.Data.ValidateSnapshot`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Data.ValidateSnapshot`  
**Category:** Data  
**Signature:** `(source_refs, transform_chain, split_defs, access_plan_inputs -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates source immutability, split-def consistency, transform-chain integrity, and namespace constraints before snapshot build.

**Operator:** `Glyphser.Data.ComputeLineageHash`  
**Category:** Data  
**Signature:** `(tenant_id, source_refs, transform_chain, split_defs -> transform_chain_hash, split_hashes, lineage_root_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes canonical lineage commitments (`transform_chain_hash`, `split_hashes`, and `lineage_root_hash`) from sorted canonical inputs.

**Operator:** `Glyphser.Data.BuildSnapshot`  
**Category:** Data  
**Signature:** `(source_refs, transform_chain, split_defs, access_plan_inputs -> dataset_snapshot_id, data_access_plan_hash)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** materializes immutable snapshot and canonical lineage metadata.

---
## 6) Procedure
```text
1. ValidateSnapshot(inputs)
2. ComputeLineageHash
3. BuildSnapshot
4. Return dataset_snapshot_id + data_access_plan_hash + lineage_report
```

---
## 7) Trace & Metrics
### Logging rule
- snapshot creation emits deterministic lineage records.
### Trace schema
- `run_header`: source_hashes, transform_chain_hash
- `iter`: step, hash, status
- `run_end`: dataset_snapshot_id
### Metric schema
- `source_count`, `transform_count`
### Comparability guarantee
- comparable iff source hashes, transforms, and split configs are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- immutable snapshots, deterministic hash serialization.
#### VII.B Operator test vectors (mandatory)
- source/transform permutations, split hash validations.
#### VII.C Golden traces (mandatory)
- golden snapshot IDs for canonical datasets.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for snapshot ID and lineage hashes.
#### VIII.B Allowed refactor categories
- storage layout changes preserving snapshot ID semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact snapshot ID compare.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- active snapshot build cursor and lineage partial hashes.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed snapshot build yields identical snapshot ID.
