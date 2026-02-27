# Glyphser Canonical Hashing Reference
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Serialization.CanonicalHashingReference`  
**Purpose (1 sentence):** Provide canonical implementation formulas and preimages for all contract-critical hashes.  
**Spec Version:** `Glyphser.Serialization.CanonicalHashingReference` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Deterministic commitment hashing.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Serialization.CanonicalHashingReference`
- **Purpose (1 sentence):** Single reference for commitment hash formulas.
### 0.A Objective Semantics
- minimize hashing drift across implementations.
### 0.B Reproducibility Contract
- hashes reproducible from canonical preimages only.
### 0.C Numeric Policy
- fixed `bytes32` digest outputs.
### 0.D Ordering and Tie-Break Policy
- all map/list orderings explicit and deterministic.
### 0.E Parallel, Concurrency, and Reduction Policy
- hash computation can parallelize only when preimage order remains fixed.
### 0.F Environment and Dependency Policy
- SHA-256 over `CBOR_CANONICAL` only.
### 0.G Operator Manifest
- `Glyphser.Serialization.ComputeDigest`
- `Glyphser.Serialization.ValidateDigestInputs`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Serialization.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(digest_table, validation_report)`.
### 0.J Spec Lifecycle Governance
- preimage change is MAJOR.
### 0.K Failure and Error Semantics
- invalid preimage fields/types fail deterministically.
### 0.L Input/Data Provenance
- each digest tied to schema version and domain tag.

---
## 2) System Model
### I.A Persistent State
- formula registry keyed by digest id.
### I.B Inputs and Hyperparameters
- digest id and preimage fields.
### I.C Constraints and Feasible Set
- all required fields must be present and typed.
### I.D Transient Variables
- normalized preimage tuples.
### I.E Invariants and Assertions
- same preimage -> same bytes32 digest.

### II.F Domain Tag and Digest Table (Normative)
- `domain_tag` is a fixed UTF-8 string bound to `digest_id` in the formula registry.
- `ComputeDigest` must prepend this exact `domain_tag` to the canonical preimage tuple.
- `digest_table` output is a canonical map: `map<digest_id:string, digest_bytes32>`, sorted lexicographically by `digest_id` before serialization.

---
## 3) Initialization
1. Load formula registry.
2. Validate digest id uniqueness.
3. Initialize computation context.

---
## 4) Operator Manifest
- `Glyphser.Serialization.ComputeDigest`
- `Glyphser.Serialization.ValidateDigestInputs`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Serialization.ValidateDigestInputs`
**Signature:** `(digest_id, preimage -> validation_report)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Validates required fields/types/order for the given `digest_id` using the formula registry.

**Operator:** `Glyphser.Serialization.ComputeDigest`  
**Signature:** `(digest_id, normalized_preimage -> digest_bytes32)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Computes `SHA-256(CBOR_CANONICAL([domain_tag, normalized_preimage]))` where `domain_tag` is loaded from the formula registry for `digest_id`.

---
## 6) Procedure
```text
1. ValidateDigestInputs
2. Normalize preimage deterministically
3. Compute digest
4. Emit digest table entry
```

---
## 7) Trace & Metrics
- Metrics: `digests_computed`, `invalid_preimages`.
- Trace includes `digest_id`, `domain_tag`, `digest_value`.

---
## 8) Validation
- vector tests for replay/checkpoint/trace/WAL/certificate digest ids.
- cross-impl byte-for-byte digest comparison vectors.

---
## 9) Refactor & Equivalence
- E0 for all digest outputs.

---
## 10) Checkpoint/Restore
- checkpoint stores formula-registry hash and last digest cursor.
- restore must produce identical digests.
