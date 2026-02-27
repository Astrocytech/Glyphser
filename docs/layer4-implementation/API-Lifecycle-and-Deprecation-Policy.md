# Glyphser API Lifecycle and Deprecation Policy
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.API.LifecyclePolicy`  
**Purpose (1 sentence):** Define customer-facing API compatibility, deprecation windows, and migration obligations.  
**Spec Version:** `Glyphser.API.LifecyclePolicy` | 2026-02-20 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`


---
## 1) Compatibility Tiers
- `stable`: backwards-compatible within MAJOR line.
- `lts`: extended support window.
- `experimental`: no long-term stability guarantee.

## 2) Deprecation Windows
- Minimum support after deprecation announcement: 18 months.
- API migration operators must be available for at least 2 MAJOR releases from announcement.

## 3) Breaking Change Requirements
- MAJOR version bump.
- migration operator and migration vectors.
- customer-facing migration guide and compatibility table update.

## 4) Service Interface Guarantees
- OpenAPI/Protobuf artifacts are normative surfaces and versioned.
- generated SDKs must remain compatible within declared window.

## 5) Normative Example
- `NextBatch -> NextBatch` transitions must declare migration operator and support window in release notes and compatibility matrix.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser API Lifecycle and Deprecation Policy" without altering existing semantics.
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
