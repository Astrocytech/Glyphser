# Glyphser Contracts Artifact Lifecycle
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.ContractsArtifactLifecycle`
**Purpose (1 sentence):** Define deterministic build, sign, publish, verify, deprecate, and retire lifecycle rules for machine-readable contract artifacts.
**Spec Version:** `Glyphser.Implementation.ContractsArtifactLifecycle` | 2026-02-19 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Artifact governance for contract integrity.

---
## 1) Scope
Applies to contract artifacts including:
- `contracts/operator_registry.cbor`
- `contracts/digest_catalog.cbor`
- `contracts/determinism_profiles.cbor`
- versioned migration and compatibility sidecar artifacts.

---
## 2) Lifecycle States (Normative)
- `DRAFT`
- `VALIDATED`
- `SIGNED`
- `PUBLISHED`
- `DEPRECATED`
- `RETIRED`

Transitions are deterministic and append-only in audit logs.

---
## 3) Deterministic Lifecycle Procedure
1. Build artifact from authoritative specs.
2. Canonicalize (CBOR canonical profile).
3. Compute root hash and schema hash.
4. Validate against lint + conformance rules.
5. Sign artifact manifest.
6. Publish immutable artifact by content hash.
7. Record publication event in trace/audit log.
8. Deprecate/retire only through explicit policy transition.

---
## 4) Required Metadata
Every artifact manifest entry must include:
- `artifact_id`
- `artifact_type`
- `artifact_version`
- `artifact_hash` (bytes32)
- `schema_hash` (bytes32)
- `signature_key_id`
- `signature_hash`
- `published_at_utc`
- `status`

---
## 5) Integrity and Retention Rules
- Artifacts are immutable once `PUBLISHED`.
- Hash mismatch is a deterministic `CONTRACT_VIOLATION`.
- `RETIRED` artifacts remain verifiable via retained manifest and signature chain.

---
## 6) Wiring References
- `docs/layer4-implementation/Operator-Registry-CBOR-Contract.md`
- `docs/layer4-implementation/Release-Evidence-Assembler.md`
- `docs/layer2-specs/Execution-Certificate.md`
- `docs/layer2-specs/Run-Commit-WAL.md`
- `docs/layer1-foundation/Digest-Catalog.md`

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser Contracts Artifact Lifecycle" without altering existing semantics.
- **Spec Version:** `Glyphser.Structural.Addendum` | 2026-02-20 | Authors: ML2ML
- **Domain / Problem Class:** Documentation governance and structural conformance.
### 0.Z EQC Mandatory Declarations Addendum
- This document inherits deterministic, numeric, and failure policies from its referenced normative contracts unless explicitly overridden.

---
## 6) Procedure
```text
1. Read and apply this document together with its referenced normative contracts.
2. Preserve deterministic ordering and evidence linkage requirements declared by those contracts.
3. Emit deterministic documentation compliance record for governance tracking.
```
