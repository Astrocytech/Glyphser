# Glyphser SDK Usage Guide Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.SDK.UsageGuide`  
**Purpose (1 sentence):** Define deterministic SDK usage patterns for syscall/service interfaces, error handling, and replay-safe client behavior.  
**Spec Version:** `Glyphser.SDK.UsageGuide` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Client integration and API correctness.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.SDK.UsageGuide`
- **Purpose (1 sentence):** Deterministic SDK integration contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: prevent client-side contract drift and non-replayable calls.
### 0.B Reproducibility Contract
- Replayable given `(operator_registry_root_hash, sdk_version, request_digest, response_digest)`.
### 0.C Numeric Policy
- Numeric payload fields must preserve declared scalar types exactly.
### 0.D Ordering and Tie-Break Policy
- Request maps and list fields must be canonicalized before digest/signature use.
### 0.E Parallel, Concurrency, and Reduction Policy
- Concurrent calls allowed; idempotent call semantics must follow registry declarations.
### 0.F Environment and Dependency Policy
- SDK must validate digests against `docs/layer1-foundation/API-Interfaces.md` and registry artifacts.
### 0.G Operator Manifest
- `Glyphser.SDK.ValidateRequest`
- `Glyphser.SDK.DispatchCall`
- `Glyphser.SDK.ValidateResponse`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.SDK.*`
### 0.I Outputs and Metric Schema
- Outputs: `(sdk_call_report, response_payload)`
- Metrics: `calls_total`, `calls_failed`, `schema_mismatch_count`
### 0.J Spec Lifecycle Governance
- SDK behavior changes affecting canonicalization are MAJOR.
### 0.K Failure and Error Semantics
- Nonconformant requests/responses fail deterministically.
### 0.L Input/Data Provenance
- Every SDK call must bind operator id, version, and resolved schema digests.

---
## 2) System Model
### I.A Persistent State
- Local interface cache and digest map.
### I.B Inputs and Hyperparameters
- operator id/version, request payload, auth context, replay context.
### I.C Constraints and Feasible Set
- Valid iff request/response match declared schemas.
### I.D Transient Variables
- call diagnostics and serialization buffers.
### I.E Invariants and Assertions
- SDK must never mutate request semantics after digest binding.

---
## 3) Initialization
1. Load operator registry and digest catalog.
2. Resolve request/response digests.
3. Validate SDK environment compatibility.

---
## 4) Operator Manifest
- `Glyphser.SDK.ValidateRequest`
- `Glyphser.SDK.DispatchCall`
- `Glyphser.SDK.ValidateResponse`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.SDK.ValidateRequest`  
**Signature:** `(operator_id, request_payload, schema_digest -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

**Operator:** `Glyphser.SDK.DispatchCall`  
**Signature:** `(operator_id, request_payload, auth_context -> response_payload)`  
**Purity class:** IO  
**Determinism:** deterministic under fixed inputs and backend state.

**Operator:** `Glyphser.SDK.ValidateResponse`  
**Signature:** `(operator_id, response_payload, schema_digest -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. ValidateRequest
2. DispatchCall
3. ValidateResponse
4. Return response_payload + sdk_call_report
```

---
## 7) Trace & Metrics
### Logging rule
- SDK calls emit deterministic request/response validation events.
### Trace schema
- `run_header`: sdk_version, operator_registry_root_hash
- `iter`: operator_id, call_id, status
- `run_end`: call_report_hash
### Metric schema
- `calls_total`, `calls_failed`, `schema_mismatch_count`
### Comparability guarantee
- Comparable iff same SDK version, registry root, and payloads.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- No calls with unresolved schema digests.
#### VII.B Operator test vectors (mandatory)
- Valid/invalid request-response fixtures.
#### VII.C Golden traces (mandatory)
- Golden SDK call traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for validated request/response hashes and error mapping.
#### VIII.B Allowed refactor categories
- SDK transport/runtime changes preserving call semantics.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of validation reports on fixed fixtures.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- SDK cache snapshot and call cursor.
### Serialization
- Canonical CBOR.
### Restore semantics
- Restored SDK state must preserve identical validation and dispatch behavior.
