# Glyphser Authorization Capability Matrix Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Security.AuthZCapabilityMatrix`  
**Purpose (1 sentence):** Define deterministic operator-to-capability authorization requirements and policy evaluation outputs.  
**Spec Version:** `Glyphser.Security.AuthZCapabilityMatrix` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** RBAC/capability enforcement and auditability.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Security.AuthZCapabilityMatrix`
- **Purpose (1 sentence):** Deterministic operator capability gating.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic authorization verdict correctness.
- Invalid objective policy: missing capability mapping is fatal.
### 0.B Reproducibility Contract
- Replayable given `(tenant_id, principal_id, operator_id, authz_policy_hash, capability_matrix_hash)`.
### 0.C Numeric Policy
- N/A except deterministic hashing and enum handling.
### 0.D Ordering and Tie-Break Policy
- Capabilities sorted lexicographically before verdict hash.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel checks allowed; final verdict is deterministic.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE`.
### 0.G Operator Manifest
- `Glyphser.Security.ResolveRequiredCapabilities`
- `Glyphser.Security.EvaluateAuthorization`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Canonical matrix source: `contracts/operator_registry.cbor`.
### 0.I Outputs and Metric Schema
- Outputs: `(authz_verdict, authz_query_hash, authz_decision_hash, authz_report)`.
### 0.J Spec Lifecycle Governance
- Capability changes for existing operator versions are MAJOR.
### 0.K Failure and Error Semantics
- Denied authorization emits deterministic failure with `authz_decision_hash`.
### 0.L Input/Data Provenance
- Operator capability mapping must be hash-bound to registry hash.

---
## 2) System Model
### I.A Persistent State
- capability matrix and role-policy bindings.
### I.B Inputs and Hyperparameters
- `tenant_id`, `principal_id`, `operator_id`, `authz_policy_hash`, `capability_matrix_hash`.
### I.C Constraints and Feasible Set
- valid iff operator is mapped and policy binding exists.
### I.D Transient Variables
- resolved capability set and diagnostics.
### I.E Invariants and Assertions
- one deterministic verdict per authorization query.

### II.F Capability Resolution Rule (Normative)
- `principal_id` format is canonical tenant-scoped UTF-8 text: `tenant_id "/" principal_local_id`.
- Delimiter constraint: `tenant_id` MUST NOT contain `"/"`; parsing is a single split on the first slash.
- Component constraints (normative):
  - `tenant_id` and `principal_local_id` MUST each be valid UTF-8 strings,
  - total encoded byte length of `tenant_id + "/" + principal_local_id` MUST be `<= 1024`.
- `principal_id` comparisons are bytewise and case-sensitive.
- `capability_matrix` MUST include immutable `matrix_version:string`; updates publish a new matrix object and `capability_matrix_hash`.
- Capability matrix canonical structure (normative):
  - canonical CBOR map: `operator_id:string -> required_capabilities:array<string>`,
  - each `required_capabilities` array is lexicographically sorted and duplicate-free.
  - `capability_matrix_hash = SHA-256(CBOR_CANONICAL(capability_matrix_map))`.
- Capability names MUST be fully-qualified and versioned (example: `storage.write.v1`).
- `required_capabilities` is read from canonical operator registry for `operator_id`.
- Missing `operator_id` mapping is deterministic failure.
- Authorization model is default-deny: any missing principal binding or missing required capability yields `DENY`.
- `authz_policy_hash` definition (normative): `SHA-256(CBOR_CANONICAL(authz_policy_document))`, where `authz_policy_document` is the canonical authorization policy mapping used for capability grants/denials.
  - `authz_policy_document` canonical schema (normative):
    - CBOR map: `principal_id:string -> granted_capabilities:array<string>`,
    - map keys (`principal_id`) sorted lexicographically,
    - each `granted_capabilities` array sorted lexicographically and duplicate-free.

### II.G Deterministic Verdict Hash (Normative)
- `authz_query_hash = SHA-256(CBOR_CANONICAL([tenant_id, [principal_id, operator_id, sorted(required_capabilities), authz_policy_hash, capability_matrix_hash]]))`.
- `granted_capabilities_hash = SHA-256(CBOR_CANONICAL(sorted(granted_capabilities)))`.
- `granted_capabilities` is the deterministic policy-evaluation output set for `(tenant_id, principal_id)` under `authz_policy_hash`, sorted lexicographically before hashing.
- `granted_capabilities` MUST NOT contain duplicate capability names (duplicate presence is deterministic failure).
- `verdict_enum` is a required enum from:
  - `ALLOW`
  - `DENY`
- `decision_reason_code` is a required enum from:
  - `ALLOW`
  - `DENY_MISSING_CAPABILITY`
  - `DENY_POLICY`
  - `DENY_PRINCIPAL_NOT_BOUND`
  - `DENY_OPERATOR_UNREGISTERED`
  - `DENY_TENANT_SCOPE`
  - `DENY_TENANT_SCOPE` semantics: authorization subject is outside allowed tenant namespace/scope for the requested operation.
- `authz_decision_hash = SHA-256(CBOR_CANONICAL([authz_query_hash, [verdict_enum, granted_capabilities_hash, decision_reason_code]]))`.
- Execution certificates MUST bind `authz_decision_hash` (not only query hash).

---
## 3) Initialization
1. Load capability matrix from registry.
2. Load tenant/principal policy bindings.
3. Validate matrix hash consistency.

---
## 4) Operator Manifest
- `Glyphser.Security.ResolveRequiredCapabilities`
- `Glyphser.Security.EvaluateAuthorization`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Security.ResolveRequiredCapabilities`  
**Category:** Security  
**Signature:** `(operator_id, registry -> required_capabilities)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** resolves sorted unique required capabilities for operator.

**Operator:** `Glyphser.Security.EvaluateAuthorization`  
**Category:** Security  
**Signature:** `(tenant_id, principal_id, operator_id, policy -> authz_verdict, authz_query_hash, authz_decision_hash, report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** evaluates capability grants and emits deterministic query/decision hashes.

---
## 6) Procedure
```text
1. ResolveRequiredCapabilities(operator_id, operator_registry)
2. EvaluateAuthorization(tenant_id, principal_id, operator_id, authz_policy)
3. Return verdict + authz_query_hash + authz_decision_hash + report
```

---
## 7) Trace & Metrics
### Logging rule
- every authorization decision emits deterministic trace event.
### Trace schema
- `run_header`: tenant_id, authz_policy_hash, capability_matrix_hash
- `iter`: principal_id, operator_id, verdict, authz_query_hash, authz_decision_hash
- `run_end`: denied_count
### Metric schema
- `allowed_count`, `denied_count`
### Comparability guarantee
- Comparable iff policy hash and capability matrix hash match.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- all callable operators have required_capabilities.
#### VII.B Operator test vectors (mandatory)
- allowed/denied capability fixtures per tenant.
#### VII.C Golden traces (mandatory)
- golden authorization decision traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for verdict, query hash, decision hash, and report.
#### VIII.B Allowed refactor categories
- policy engine refactors preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of verdict/authz hash.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- policy snapshot hash and decision cursor.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed authorization yields identical outcomes.
