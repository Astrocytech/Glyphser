# Glyphser Evidence Catalog
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Release.EvidenceCatalog`
**Purpose (1 sentence):** Define the authoritative evidence artifact catalog with schema, producer, verifier, and gate bindings.
**Spec Version:** `Glyphser.Release.EvidenceCatalog` | 2026-02-21 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Release.EvidenceCatalog`
- **Purpose (1 sentence):** Deterministic evidence catalog contract.
- **Spec Version:** `Glyphser.Release.EvidenceCatalog` | 2026-02-21 | Authors: Olejar Damir
- **Domain / Problem Class:** evidence governance and external verifiability.
### 0.A Objective Semantics
- Every trust claim must map to a deterministic evidence artifact and verifier.
### 0.B Reproducibility Contract
- Replayable given `(evidence_catalog_version, artifact_refs, verifier_versions)`.
### 0.C Numeric Policy
- N/A.
### 0.D Ordering and Tie-Break Policy
- Catalog entries are ordered by `artifact_id` ascending UTF-8 bytewise.
### 0.E Parallel, Concurrency, and Reduction Policy
- Validation may run in parallel; verdict merge is fail-dominant.
### 0.F Environment and Dependency Policy
- Canonical serialization profile: `CanonicalSerialization`.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Release.CollectEvidence`
- `Glyphser.Release.ValidateEvidenceBundle`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Evidence bundle path namespace: `release/evidence/<release_id>/`.
### 0.I Outputs and Metric Schema
- Outputs: `(evidence_catalog_report, evidence_catalog_hash)`.
### 0.J Spec Lifecycle Governance
- Catalog schema changes are MAJOR-governed.
### 0.K Failure and Error Semantics
- Missing mandatory artifact is deterministic failure.
### 0.L Input/Data Provenance
- Evidence producers must emit content-addressed artifacts.
### 0.Z EQC Mandatory Declarations Addendum
- `stochastic_used: false`
- `seed_space: N/A`
- `prng_family: N/A`
- `determinism_level: BITWISE`

## 2) Artifact Catalog (Normative)
| artifact_id | schema_ref | producer | verifier | referenced_by | failure_codes |
|---|---|---|---|---|---|
| `execution_certificate` | `docs/layer2-specs/Execution-Certificate.md` | `Glyphser.Certificate.WriteExecutionCertificate` | `Glyphser.Security.VerifyCertificate` | release gates, audit exports | `CONTRACT_VIOLATION`, `SIGNATURE_MISMATCH` |
| `trace_sidecar` | `docs/layer2-specs/Trace-Sidecar.md` | `Glyphser.IO.WriteTape` | `Glyphser.Replay.CompareTrace` | certificate payload, replay, release gates | `CONTRACT_VIOLATION`, `TRACE_SCHEMA_INVALID` |
| `checkpoint_manifest` | `docs/layer2-specs/Checkpoint-Schema.md` | `Glyphser.IO.SaveCheckpoint` | `Glyphser.Checkpoint.Restore` | certificate payload, replay, recovery proofs | `CONTRACT_VIOLATION`, `CHECKPOINT_INVALID` |
| `policy_transcript` | `docs/layer2-specs/Monitoring-Policy.md` | `Glyphser.Policy.Evaluate` | `Glyphser.Monitor.DriftCompute` | `policy_gate_hash`, release gates | `CONTRACT_VIOLATION`, `POLICY_VIOLATION` |
| `adapter_cert_bundle` | `docs/layer4-implementation/Third-Party-Operator-Certification-Program.md` | conformance harness | `Glyphser.Release.ValidateEvidenceBundle` | enterprise/regulated gates | `CERT_BUNDLE_INVALID` |
| `chaos_recovery_proof_pack` | `docs/layer3-tests/Failure-Injection-Scenarios.md` | chaos harness | release gate verifier | regulated release gate | `RECOVERY_OUTCOME_MISMATCH` |
| `perf_baseline_bundle` | `docs/layer3-tests/Performance-Plan.md` | perf harness | `Glyphser.Perf.EvaluateRegressionPolicy` | performance gate | `PERF_REGRESSION` |

## 3) Catalog Hash (Normative)
- `evidence_catalog_hash = SHA-256(CBOR_CANONICAL(["evidence_catalog", entries]))`.

## 4) Cross-References
- `docs/layer4-implementation/Release-Evidence-Assembler.md`
- `docs/layer3-tests/Release-Gates.md`
- `docs/layer2-specs/Execution-Certificate.md`
- `docs/layer2-specs/Trace-Sidecar.md`

## 6) Procedure
```text
1. Load required artifacts for target release profile.
2. Validate each artifact against schema_ref and verifier.
3. Record deterministic pass/fail with failure code mapping.
4. Compute evidence_catalog_hash and emit catalog report.
```
