# Glyphser Digest Catalog Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Registry.DigestCatalog`  
**Purpose (1 sentence):** Define an authoritative catalog mapping digest labels to full bytes32 values and deterministic resolution rules.  
**Spec Version:** `Glyphser.Registry.DigestCatalog` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Digest governance and consistency control.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Registry.DigestCatalog`
- **Purpose (1 sentence):** Canonical digest label-to-bytes32 mapping.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: exact digest lookup and equality.
- Invalid objective policy: unresolved label is fatal.
### 0.B Reproducibility Contract
- Replayable given `(catalog_version, catalog_hash)`.
- `catalog_version` is a positive integer schema-version value carried inside the catalog object (`catalog_version >= 1`).
### 0.C Numeric Policy
- Digests are fixed-length `bytes32`.
### 0.D Ordering and Tie-Break Policy
- Records sorted lexicographically by `digest_label`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Lookup is pure read-only.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE`.
### 0.G Operator Manifest
- `Glyphser.Registry.ResolveDigestRef`
- `Glyphser.Registry.ValidateDigestCatalog`
- `Glyphser.Error.Emit`
  - Note: `Glyphser.Error.Emit` is a shared runtime error operator defined in the core error contract (`docs/layer1-foundation/Error-Codes.md`), not redefined in this document.
### 0.H Namespacing and Packaging
- Canonical location: `contracts/digest_catalog.cbor`.
### 0.I Outputs and Metric Schema
- `ResolveDigestRef` output: `(resolved_digest)`.
- `ValidateDigestCatalog` output: `(validation_report)`.
### 0.J Spec Lifecycle Governance
- Label removal is MAJOR.
### 0.K Failure and Error Semantics
- Abort on unresolved or duplicate labels.
### 0.L Input/Data Provenance
- Catalog is content-addressed and immutable.

---
## 2) System Model
### I.A Persistent State
- `digest_catalog`.
### I.B Inputs and Hyperparameters
- `digest_ref` and catalog blob.
- `catalog_version:uint32` (required field of catalog object; versioned by this contract, not inferred externally; must be `>= 1`).
### I.C Constraints and Feasible Set
- Valid iff labels unique, digests are bytes32, and `catalog_version:uint32` is present.
- `digest_label` MUST match `^[a-z0-9_\\-\\.]{1,128}$` and MUST NOT match `^[0-9a-f]{64}$` (reserved for inline digest form).
- Label uniqueness uses exact bytewise UTF-8 comparison (case-sensitive, no trimming/normalization).
### I.D Transient Variables
- resolution diagnostics.
### I.E Invariants and Assertions
- no duplicate labels.
- no additional fields in entry records.

### II.F Digest Catalog Schema (Normative)
- Catalog object schema:
  - `catalog_version:uint32`
  - `entries:array<entry_record>`
- `entry_record` serialization is canonical CBOR map with exactly the fields below (no extras, no omissions):
  - `digest_label:string`
  - `digest_value:bytes32`
  - `algorithm:string` (must be `sha256`)
  - `domain_tag:string` (domain metadata for governance/audit; does not alter `ResolveDigestRef` lookup semantics).
- Additional fields are forbidden in both catalog object and entry records.
- Canonical CBOR in this document means `CBOR_CANONICAL` as defined by `docs/layer1-foundation/Canonical-CBOR-Profile.md` (single authoritative encoding profile for commitment paths).

### II.H Catalog Commitment (Normative)
- `entries_sorted` are sorted by `digest_label` ascending (bytewise UTF-8, case-sensitive).
- `catalog_version` is encoded as CBOR unsigned integer (`uint32` domain constraint).
- `catalog_hash = SHA-256(CBOR_CANONICAL(["digest_catalog", [catalog_version, entries_sorted]]))`.
- Any document using `sha256:<label>` references is valid only against the committed `catalog_hash`.

### II.G Resolution Rule (Normative)
- `digest_ref` supports two forms:
  - inline: `sha256:<hex64>` where `<hex64>` is exactly 64 hex chars and resolves directly to bytes32,
  - catalog label: `sha256:<label>` where `<label>` must exist in catalog and resolve to bytes32.
- Disambiguation rule:
  - if tail matches `^[0-9a-fA-F]{64}$`, treat as inline bytes32 digest,
  - otherwise treat as catalog label and perform lookup.
- Inline digest tail MAY be uppercase or lowercase; implementations MUST normalize inline hex tails to lowercase before bytes parsing and validation.
- Signature/hash computations must use resolved bytes32 digest bytes, never label string bytes.

---
## 3) Initialization
1. Load digest catalog.
2. Validate schema and uniqueness.
3. Build lookup index.
4. Compute and store `catalog_hash` using §II.H exactly:
   - `catalog_hash = SHA-256(CBOR_CANONICAL(["digest_catalog", [catalog_version, entries_sorted]]))`,
   - where `entries_sorted` is the catalog `entries` array sorted by `digest_label` ascending (bytewise UTF-8, case-sensitive).

---
## 4) Operator Manifest
- `Glyphser.Registry.ResolveDigestRef`
- `Glyphser.Registry.ValidateDigestCatalog`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Registry.ResolveDigestRef`  
**Category:** Governance  
**Signature:** `(digest_ref, digest_catalog -> digest_value)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** resolves digest labels to bytes32 values.

**Operator:** `Glyphser.Registry.ValidateDigestCatalog`  
**Category:** Governance  
**Signature:** `(digest_catalog -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates schema, uniqueness, label constraints, and commitment computability.
**validation_report (minimum schema):**
```yaml
validation_report:
  is_valid: bool
  errors: [string]         # deterministic order
  catalog_hash: bytes32    # present when is_valid=true
```

---
## 6) Procedure
```text
1. ResolveDigestRef using initialized validated catalog index.
2. Return digest_value
```

---
## 7) Trace & Metrics
### Logging rule
- digest reference resolutions emit deterministic events.
### Trace schema
- `run_header`: catalog_hash
- `iter`: digest_ref, status
- `run_end`: resolved_digest
### Trace status enum
- `status` MUST be one of:
  - `resolved`
  - `missing`
### Metric schema
- `resolved_count`, `missing_count`
### Comparability guarantee
- Comparable iff catalog hash is identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- no duplicate labels.
- all labels MUST satisfy format constraints in §I.C.
- cross-document label resolution checks (ensuring every `sha256:<label>` reference resolves in catalog) are enforced by spec-lint tooling, not catalog-internal schema validation.
#### VII.B Operator test vectors (mandatory)
- valid/missing/duplicate label cases.
#### VII.C Golden traces (mandatory)
- golden resolution traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for digest resolution outputs.
#### VIII.B Allowed refactor categories
- indexing optimizations preserving output.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of resolved bytes32.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- catalog hash only (catalog is immutable and lookup is stateless in this contract).
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- identical resolution on resume.
