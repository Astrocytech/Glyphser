# Glyphser Data Contract Fuzzing Guide
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Test.DataContractFuzzing`  
**Purpose (1 sentence):** Define deterministic fuzzing strategy for contract-critical parsers, validators, and canonicalization paths.  
**Spec Version:** `Glyphser.Test.DataContractFuzzing` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Robustness testing and parser hardening.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Test.DataContractFuzzing`
- **Purpose (1 sentence):** Deterministic fuzzing contract for data/schema parsers.
### 0.A Objective Semantics
- minimize parser crashes, undefined behavior, and non-deterministic parse outcomes.
### 0.B Reproducibility Contract
- fuzz outcomes reproducible from `(fuzz_seed, harness_version, target_schema_hash)`.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- exact counters for crashes and unique findings.
### 0.D Ordering and Tie-Break Policy
- findings sorted by `(target, signature, first_seen_input_hash)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- fuzz workers parallelized; findings de-duplicated deterministically.
### 0.F Environment and Dependency Policy
- fuzz runtime pinned with sanitizer profile.
### 0.G Operator Manifest
- `Glyphser.Test.GenerateFuzzInput`
- `Glyphser.Test.RunFuzzTarget`
- `Glyphser.Test.DeduplicateFindings`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Test.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(fuzz_report, findings_catalog_hash)`.
### 0.J Spec Lifecycle Governance
- target set changes are MAJOR.
### 0.K Failure and Error Semantics
- crash or sanitizer violation is a deterministic failing finding.
### 0.L Input/Data Provenance
- fuzz corpora and generated inputs are hash-addressed.
### 0.Z EQC Mandatory Declarations Addendum
- seed space: `uint64`.
- PRNG family: `Philox4x32-10`.
- replay guarantee: identical `(fuzz_seed, harness_version, target_schema_hash, iteration_budget)` yields identical `findings_catalog_hash` and deterministic finding identities.
- floating-point format: IEEE-754 binary64 only for summary metrics; verdict path is hash/counter based.
- NaN/Inf policy: prohibited in metric outputs; deterministic failure if produced.
- default tolerances: N/A for crash/violation verdicts.
- determinism target: E0 for `findings_catalog_hash` and unique finding set.

---
## 2) System Model
### I.A Persistent State
- fuzz corpus index and findings registry.
### I.B Inputs and Hyperparameters
- fuzz seed, target list, iteration budget.
### I.C Constraints and Feasible Set
- all targets must expose deterministic parse/validate API.
### I.D Transient Variables
- generated input bytes and target outputs.
### I.E Invariants and Assertions
- same input bytes must yield same target verdict.

---
## 3) Initialization
1. Load fuzz target inventory.
2. Initialize corpus and seed.
3. Initialize findings store.

---
## 4) Operator Manifest
- `Glyphser.Test.GenerateFuzzInput`
- `Glyphser.Test.RunFuzzTarget`
- `Glyphser.Test.DeduplicateFindings`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Test.GenerateFuzzInput`
**Signature:** `(target_id, fuzz_seed, corpus_cursor -> input_bytes, corpus_cursor_next)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** deterministically generates fuzz input bytes from seed+corpus state.
**allowed_error_codes:** `CONTRACT_VIOLATION`.

**Operator:** `Glyphser.Test.RunFuzzTarget`  
**Signature:** `(target_id, input_bytes -> target_result)`  
**Purity class:** IO  
**Determinism:** deterministic for identical input bytes  
**Definition:** Executes one fuzz target invocation and records verdict/crash metadata.
**Preconditions / Postconditions:** target exists; input bytes are bounded by target contract.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `FUZZ_TARGET_CRASH`, `SANITIZER_VIOLATION`.

**Operator:** `Glyphser.Test.DeduplicateFindings`
**Signature:** `(findings -> deduped_findings, findings_catalog_hash)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** deduplicates findings by canonical key and emits `findings_catalog_hash`.
**allowed_error_codes:** `CONTRACT_VIOLATION`.

---
## 6) Procedure
```text
1. Generate deterministic fuzz inputs
2. Execute selected target(s)
3. Capture crashes/violations
4. Deduplicate findings and compute `findings_catalog_hash`
5. Emit report `(fuzz_report, findings_catalog_hash)`
```

---
## 7) Trace & Metrics
- Metrics: `inputs_tested`, `crashes`, `violations`, `unique_findings`.
- Trace includes target id, input hash, verdict signature.

---
## 8) Validation
- fuzz harness self-tests with known crash fixtures.
- deterministic deduplication tests.

---
## 9) Refactor & Equivalence
- E0 for unique finding set and findings catalog hash.

---
## 10) Checkpoint/Restore
- checkpoint stores `corpus_cursor`, `iterations_completed`, `dedup_state_hash`, and current `findings_catalog_hash`.
- restore resumes fuzzing deterministically.
