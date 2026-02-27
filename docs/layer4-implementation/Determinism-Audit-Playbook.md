# Glyphser Determinism Audit Playbook
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Replay.DeterminismAuditPlaybook`
**Purpose (1 sentence):** Consolidate determinism verification rules, evidence bindings, and failure taxonomy for external audits.
**Spec Version:** `Glyphser.Replay.DeterminismAuditPlaybook` | 2026-02-21 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Replay.DeterminismAuditPlaybook`
- **Purpose (1 sentence):** Determinism evidence audit playbook.
- **Spec Version:** `Glyphser.Replay.DeterminismAuditPlaybook` | 2026-02-21 | Authors: Olejar Damir
- **Domain / Problem Class:** reproducibility auditing.
### 0.A Objective Semantics
- Map determinism profile rules to observable evidence and deterministic failures.
### 0.B Reproducibility Contract
- Replayable given `(replay_token, determinism_profile_hash, trace_final_hash, checkpoint_hash, certificate_hash)`.
### 0.C Numeric Policy
- E1 tolerances from active profile; default fallback from replay contract.
### 0.D Ordering and Tie-Break Policy
- First divergence is earliest by `(t, operator_seq, field_path)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-run comparison allowed; summaries reduce deterministically.
### 0.F Environment and Dependency Policy
- Requires env/toolchain hash lock and registry root lock.
### 0.G Operator Manifest
- `Glyphser.Replay.CompareTrace`
- `Glyphser.Replay.VerifyReplayToken`
- `Glyphser.Certificate.VerifyBoundHashes`
### 0.H Namespacing and Packaging
- Audit package path: `audit/determinism/<run_id>/`.
### 0.I Outputs and Metric Schema
- Outputs: `(determinism_audit_report, failure_digest_hash)`.
### 0.J Spec Lifecycle Governance
- Failure digest schema is MAJOR-governed.
### 0.K Failure and Error Semantics
- Determinism violations emit deterministic failure digest.
### 0.L Input/Data Provenance
- Inputs from replay, trace, checkpoint, certificate, error-code contracts.

## 2) Profile-to-Evidence Mapping (Normative)
| profile_rule | evidence_fields | verifier |
|---|---|---|
| `E0 bitwise identity` | `trace_final_hash`, `checkpoint_hash`, critical field bytes | `Glyphser.Replay.CompareTrace` |
| `E1 tolerance` | field-level tolerances + compared values | `Glyphser.Replay.CompareTrace` |
| replay token binding | `replay_token`, `manifest_hash`, `env_manifest_hash` | `Glyphser.Replay.VerifyReplayToken` |
| certificate consistency | bound hashes in signed payload | `Glyphser.Security.VerifyCertificate` |

## 3) Failure Digest (Normative)
- `failure_digest = {failure_code, first_divergence_operator, first_divergence_path, trace_hash_lhs, trace_hash_rhs, evidence_refs}`.
- `failure_digest_hash = SHA-256(CBOR_CANONICAL(["failure_digest", failure_digest]))`.

## 4) Error Taxonomy Reference
- Authoritative codes: `docs/layer1-foundation/Error-Codes.md`.

## 5) Operator Definitions
**Operator:** `Glyphser.Replay.VerifyReplayToken`
**Signature:** `(replay_token, manifest_hash, env_manifest_hash, policy_bundle_hash, determinism_profile_hash, operator_contracts_root_hash, driver_runtime_fingerprint_hash, seed -> replay_token_report)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Recomputes expected replay-token commitment from bound inputs, compares bytewise with provided `replay_token`, and emits deterministic pass/fail with mismatch diagnostics.

**Operator:** `Glyphser.Certificate.VerifyBoundHashes`
**Signature:** `(execution_certificate, manifest_hash, trace_final_hash, checkpoint_hash, policy_bundle_hash, determinism_profile_hash, operator_contracts_root_hash -> bound_hash_report)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Verifies certificate signed-payload bound hash fields against provided evidence identities and emits deterministic pass/fail report.

## 6) Procedure
```text
1. Verify replay-token and environment/registry bindings.
2. Compare trace/checkpoint/certificate commitments by profile rule.
3. Locate first deterministic divergence.
4. Emit determinism_audit_report and failure_digest_hash.
```
