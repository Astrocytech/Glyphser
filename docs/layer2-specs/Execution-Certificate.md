# Glyphser Execution Certificate Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Certificate.ExecutionCertificate`  
**Purpose (1 sentence):** Define a signed proof-carrying execution certificate that gates registry, deployment, and audit workflows.  
**Spec Version:** `Glyphser.Certificate.ExecutionCertificate` | 2026-02-18 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Verifiable execution provenance and policy gating.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Certificate.ExecutionCertificate`
- **Purpose (1 sentence):** Kernel-issued execution proof contract.
- **Spec Version:** `Glyphser.Certificate.ExecutionCertificate` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Signed execution evidence.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize unverifiable releases and non-auditable promotions.
### 0.B Reproducibility Contract
- Replayable given `(manifest_hash, trace_final_hash, checkpoint_hash, determinism_profile_hash, policy_bundle_hash)`.
### 0.C Numeric Policy
- Hashes/signatures exact bytes; no tolerance path.
### 0.D Ordering and Tie-Break Policy
- Certificate fields serialized in canonical key order.
### 0.E Parallel, Concurrency, and Reduction Policy
- One certificate per run_id; promotion checks deterministic across replicas.
### 0.F Environment and Dependency Policy
- `trust_mode: "SOFTWARE_ONLY" | "ATTESTED"` (default `SOFTWARE_ONLY`).
### 0.G Operator Manifest
- `Glyphser.Certificate.Build`
- `Glyphser.Certificate.Sign`
- `Glyphser.Certificate.Verify`
- `Glyphser.Certificate.EvidenceValidate`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Certificate.*` operators are global governance operators.
### 0.I Outputs and Metric Schema
- Outputs: `(execution_certificate, verification_report)`
- Metrics: `certificate_valid`, `evidence_link_coverage`
- Completion status: `success | failed`
### 0.J Spec Lifecycle Governance
- Field additions are MINOR; required-field removals/changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on invalid signature/evidence mismatch.
### 0.L Input/Data Provenance
- Certificate must bind manifest, trace, checkpoint, sampler, DP, TMMU, backend, and attestation evidence.

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
- certificate registry and trust roots.
### I.B Inputs and Hyperparameters
- `tenant_id`, `run_id`, `replay_token`, `manifest_hash`, `trace_final_hash`, `checkpoint_hash`, `policy_bundle_hash`, `security_policy_hash?`, `authz_policy_hash?`, `monitor_policy_hash?`, `dp_policy_hash?`, `redaction_policy_hash?`, `dependencies_lock_hash`, `determinism_profile_hash`, `operator_contracts_root_hash`, `ir_hash`, `lineage_root_hash`, `dp_accountant_state_hash?`, `sampler_config_hash`, `data_access_plan_hash`, `dataset_snapshot_id`, `tmmu_plan_hash`, `backend_binary_hash`, `lockfile_hash`, `toolchain_hash`, `attestation_bundle_hash?`, `attestation_quote_hash?`, `redaction_key_id?`.
### I.C Constraints and Feasible Set
- Registry/deploy actions are invalid without a valid certificate.
### I.D Transient Variables
- evidence bundle hash, signature payload, verification diagnostics.
### I.E Invariants and Assertions
- One certificate signs one immutable evidence tuple.

### II.F ExecutionCertificate Structure (Normative)
- Canonical object:
  - `signed_payload` (canonical CBOR; this exact payload is signed)
  - `unsigned_metadata` (not signed; informational only)
- `signed_payload` field set is fixed by this section; no additional implementation-specific fields are allowed in signed bytes.
- policy-bundle consistency rule:
  - if individual policy hashes are present (`security/authz/monitor/dp/redaction`), they MUST match the decomposition of `policy_bundle_hash` under `policy_bundle`; mismatch is deterministic verification failure.
- Dependency identity semantics:
  - `lockfile_hash` = canonical package lock digest (`LockfileDigest`).
  - `dependencies_lock_hash` = derived environment-bound commitment (`DependenciesLockDigest`).
  - `operator_contracts_root_hash` = `operator_registry_root_hash` from `docs/layer1-foundation/Operator-Registry-Schema.md`.
  - `certificate_hash = SHA-256(certificate_cbor)` where `certificate_cbor` is canonical serialized certificate object (signed payload + signature envelope).
- `signed_payload` required fields:
  - `certificate_version:string`
  - `tenant_id:string`
  - `run_id:string`
  - `replay_token:bytes32`
  - `manifest_hash:bytes32`
  - `trace_final_hash:bytes32`
  - `checkpoint_hash:bytes32`
  - `policy_bundle_hash:bytes32`
  - `security_policy_hash?:bytes32`
  - `authz_policy_hash?:bytes32`
  - `monitor_policy_hash?:bytes32`
  - `dp_policy_hash?:bytes32`
  - `policy_gate_hash:bytes32`
    - semantics: hash of the canonical policy-gate evaluation transcript for the certified run context, as defined in `docs/layer2-specs/Monitoring-Policy.md` (section II.G).
  - `authz_decision_hash:bytes32`
    - provenance note: full authorization context (`authz_query_hash`, verdict, reason, granted set) is carried in trace/audit records; certificate stores `authz_decision_hash` for cryptographic cross-linking.
  - `dependencies_lock_hash:bytes32`
  - `lockfile_hash:bytes32`
  - `toolchain_hash:bytes32`
  - `determinism_profile_hash:bytes32`
  - `operator_contracts_root_hash:bytes32`
  - `ir_hash:bytes32`
  - `lineage_root_hash:bytes32`
  - `redaction_policy_hash?:bytes32`
  - `redaction_key_id?:string`
  - `sampler_config_hash:bytes32`
  - `data_access_plan_hash:bytes32`
  - `dataset_snapshot_id:string`
  - `tmmu_plan_hash:bytes32`
  - `backend_binary_hash:bytes32`
  - `dp_epsilon?:float64`
  - `dp_delta?:float64`
  - `dp_accountant_state_hash?:bytes32` (if DP enabled; equals `SHA-256(CBOR_CANONICAL(accountant_state_t))` from `docs/layer2-specs/DifferentialPrivacy-Apply.md`)
  - `attestation_quote_hash?:bytes32` (required in `ATTESTED` mode)
  - `attestation_bundle_hash?:bytes32` (required in `ATTESTED` mode)
  - `trust_store_hash:bytes32`
  - `key_id:string`
  - `signature_algorithm:string` (e.g., `"ed25519"`)
  - `revocation_bundle_hash:bytes32`
  - `verification_time_utc:string` (required when online revocation/attestation checks are verdict-affecting)
  - `valid_until_utc:string` (certificate expiry upper bound for verifier acceptance)
  - `determinism_conformance_suite_id?:bytes32`
  - `step_start:uint64`
  - `step_end:uint64`
  - semantics: `step_start`/`step_end` are the inclusive first/last step indices covered by this certificate; final run certificate covers the full run interval.
  - zero-step convention: for runs that execute zero steps, set `step_start=0` and `step_end=0`.
- `unsigned_metadata` optional fields:
  - `wall_time_start_utc:string`
  - `wall_time_end_utc:string`
  - operational notes/audit pointers
- Envelope:
  - `signature:bytes64`
- Signature scheme (normative):
  - canonical payload serialization: canonical CBOR of `signed_payload`
  - signature algorithm: indicated by `signed_payload.signature_algorithm`; current required value is `"ed25519"`
  - Ed25519 implementation MUST follow RFC 8032 deterministic signing behavior (no external nonce randomness).
- Trust/revocation commitment definitions:
  - `trust_store_hash = SHA-256(CBOR_CANONICAL(trust_store_bundle))`, where `trust_store_bundle` is the canonical root/intermediate key set used for verification.
  - `revocation_bundle_hash = SHA-256(CBOR_CANONICAL(revocation_bundle))`, where `revocation_bundle` is the canonical CRL/OCSP capture (online) or pinned offline revocation set.
  - Normative source definitions are aligned with `docs/layer2-specs/Security-Compliance-Profile.md`.
  - Time-sensitive verification checks MUST use signed `verification_time_utc` as the evaluation time anchor (not verifier wall-clock time).
  - Timestamp canonical format (normative): UTC ISO 8601 without fractional seconds, exactly `YYYY-MM-DDTHH:MM:SSZ` (example: `2026-02-20T15:04:05Z`) for `verification_time_utc` and `valid_until_utc`.
  - `key_id` MUST be globally unique within trust-store scope and map to exactly one public key at verification time.

---
## 3) Initialization
1. Load trust mode and signing policy.
2. Validate required evidence hashes.
3. Build canonical signing payload.

---
## 4) Operator Manifest
- `Glyphser.Certificate.Build`
- `Glyphser.Certificate.Sign`
- `Glyphser.Certificate.Verify`
- `Glyphser.Certificate.EvidenceValidate`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
External operator reference: `Glyphser.Error.Emit` is defined in `docs/layer1-foundation/Error-Codes.md`.

**Operator:** `Glyphser.Certificate.Build`  
**Category:** Security  
**Signature:** `(evidence_bundle -> certificate_payload)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical payload construction from evidence tuple.

**Operator:** `Glyphser.Certificate.Sign`  
**Category:** Security  
**Signature:** `(certificate_payload, signing_key_ref -> execution_certificate)`  
**Purity class:** IO  
**Determinism:** deterministic payload + deterministic signature algorithm policy  
**Definition:** signs canonical CBOR bytes of `signed_payload` only; `unsigned_metadata` is excluded. In `ATTESTED` mode key release requires attestation policy pass. `signing_key_ref` may resolve to HSM/KMS key material via daemon key broker; signer MUST enforce deterministic algorithm behavior for the selected `signature_algorithm`.

**Operator:** `Glyphser.Certificate.Verify`  
**Category:** Security  
**Signature:** `(execution_certificate, trust_store -> verification_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** verifies signature over `signed_payload`, required field presence, trust chain, signer key validity window, expiry (`verification_time_utc <= valid_until_utc`), and revocation status using `revocation_bundle_hash`.

**Operator:** `Glyphser.Certificate.EvidenceValidate`  
**Category:** Security  
**Signature:** `(manifest, trace, checkpoint, replay_context -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates pre-sign cross-artifact coherence and rejects mismatched evidence.

---
## 6) Procedure
```text
1. Build(evidence_bundle)
2. Sign(payload, signing_key_ref)
3. Verify(certificate, trust_store)
4. EvidenceValidate(manifest, trace, checkpoint, replay_context)
5. Return certificate + report
```

---
## 7) Trace & Metrics
### Logging rule
- Every certificate issuance and verification emits deterministic events.
### Trace schema
- `run_header`: certificate_version, trust_mode
- `iter`: run_id, certificate_hash, verify_status
- `run_end`: evidence_validation_status
### Metric schema
- `certificate_valid`, `evidence_mismatch_count`
### Comparability guarantee
- Comparable iff certificate schema, trust roots, and evidence validation rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- required fields complete, signature present, deterministic serialization.
#### VII.B Operator test vectors (mandatory)
- valid signature, invalid signature, missing required evidence, mismatched hash tests.
#### VII.C Golden traces (mandatory)
- golden certificate verification traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for certificate bytes and verification verdict.
#### VIII.B Allowed refactor categories
- cryptographic implementation updates preserving inputs/outputs and trust policy.
#### VIII.C Equivalence test procedure (mandatory)
- byte-level compare + deterministic verdict compare.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- last verified certificate hash and trust context hash.
### Serialization
- deterministic CBOR.
### Restore semantics
- restored verifier produces identical verdict on identical evidence bundle.

---
## 11) Trust Report and Human-Auditable Outputs (Normative)
- `Verify` MUST produce a stable trust report projection in addition to binary verdict:
  - trust roots used,
  - revocation mode/status,
  - attestation verification status,
  - policy gate linkage status,
  - authorization linkage status.
- Trust report identity:
  - `trust_report_hash = SHA-256(CBOR_CANONICAL(trust_report))`.
- Regulated profile certificate evidence MUST include:
  - `chaos_recovery_proof_pack_hash` when recovery scenarios are required by policy.
