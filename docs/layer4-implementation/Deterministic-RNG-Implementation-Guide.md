# Glyphser Deterministic RNG Implementation Guide
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.DeterministicRNGGuide`  
**Purpose (1 sentence):** Define deterministic RNG implementation rules across kernel, data, model, and DP operators.  
**Spec Version:** `Glyphser.Implementation.DeterministicRNGGuide` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** RNG determinism and replay.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.DeterministicRNGGuide`
- **Purpose (1 sentence):** Deterministic RNG implementation contract.
### 0.A Objective Semantics
- minimize RNG divergence and ownership violations.
### 0.B Reproducibility Contract
- reproducible given `(seed, rng_policy_hash, operator_id, rng_offsets)`.
### 0.C Numeric Policy
- counters and offsets are uint64 exact.
### 0.D Ordering and Tie-Break Policy
- RNG draws ordered by canonical operator execution sequence.
### 0.E Parallel, Concurrency, and Reduction Policy
- substreams deterministic by `(rank, operator_seq, tensor_index)`.
### 0.F Environment and Dependency Policy
- pinned PRNG implementation and version.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Random.InitializePRNG`
- `Glyphser.Random.DeriveSubstream`
- `Glyphser.Random.ConsumeDeterministic`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Random.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(rng_report, offset_audit)`.
### 0.J Spec Lifecycle Governance
- PRNG family change is MAJOR.
### 0.K Failure and Error Semantics
- unauthorized RNG consumption is fatal.
### 0.L Input/Data Provenance
- RNG state transitions must be trace-bound.

---
## 2) System Model
### I.A Persistent State
- RNG root state and per-operator offset table.
### I.B Inputs and Hyperparameters
- seed, operator id, rank, stream id.
### I.C Constraints and Feasible Set
- stochastic ops only; pure ops must not consume RNG.
### I.D Transient Variables
- substream keys and counters.
### I.E Invariants and Assertions
- monotonic offset progression per stream.

---
## 3) Initialization
1. Initialize root RNG state.
2. Bind deterministic substream policy.
3. Initialize offset audit log.

---
## 4) Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Random.InitializePRNG`
- `Glyphser.Random.DeriveSubstream`
- `Glyphser.Random.ConsumeDeterministic`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Random.DeriveSubstream`  
**Signature:** `(root_state, operator_id, rank, operator_seq -> substream_state)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Derives deterministic substream state by canonical tuple hashing.

---
## 6) Procedure
```text
1. Initialize root RNG
2. Derive per-operator substream
3. Consume draws with offset tracking
4. Emit RNG audit and fail on ownership violations
```

---
## 7) Trace & Metrics
- Metrics: `rng_draws_total`, `rng_violations`, `max_offset`.
- Trace includes `rng_offset_before`, `rng_offset_after`, `operator_id`.

---
## 8) Validation
- golden RNG vectors for seed/substream/draw outputs.
- ownership violation tests.

---
## 9) Refactor & Equivalence
- E0 for generated random streams and offsets.

---
## 10) Checkpoint/Restore
- checkpoint stores root RNG state and per-stream offsets.
- restore must resume identical draw sequences.
