# Glyphser Release Evidence Assembler Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Release.EvidenceAssembler`  
**Purpose (1 sentence):** Define deterministic assembly of release evidence bundles consumed by certificate signing and deployment gates.  
**Spec Version:** `Glyphser.Release.EvidenceAssembler` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Release governance and evidence binding.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Release.EvidenceAssembler`
- **Purpose (1 sentence):** Deterministic release evidence assembly contract.
### 0.A Objective Semantics
- minimize missing or inconsistent release evidence.
### 0.B Reproducibility Contract
- evidence bundle reproducible from `(release_manifest_hash, artifact_hash_set, assembly_policy_hash)`.
### 0.C Numeric Policy
- hash-based commitments only.
### 0.D Ordering and Tie-Break Policy
- evidence entries sorted by `(evidence_type, evidence_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- evidence fetches parallel; final assembly deterministic.
### 0.F Environment and Dependency Policy
- assembler runtime and policy pinned.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Release.CollectEvidenceRefs`
- `Glyphser.Release.BuildEvidenceBundle`
- `Glyphser.Release.ValidateEvidenceBundle`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Release.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(evidence_bundle_ref, evidence_bundle_hash, validation_report)`.
### 0.J Spec Lifecycle Governance
- required evidence field changes are MAJOR.
### 0.K Failure and Error Semantics
- missing mandatory evidence fails assembly.
### 0.L Input/Data Provenance
- all evidence refs must be content-addressed.

---
## 2) System Model
### I.A Persistent State
- evidence policy catalog and assembler version.
### I.B Inputs and Hyperparameters
- release manifest, trace/checkpoint/certificate refs, registry refs.
 - optional external-verification artifacts:
   - certification evidence bundles (backend/store),
   - observability mapping bundle hash,
   - performance tier baseline artifacts,
   - chaos/recovery proof packs.
### I.C Constraints and Feasible Set
- mandatory evidence set must be complete.
### I.D Transient Variables
- resolved evidence rows and validation diagnostics.
### I.E Invariants and Assertions
- bundle hash uniquely identifies assembled evidence set.
- external-verification-ready releases MUST include certification and observability evidence when target profile is `enterprise` or `regulated`.

### II.F External Verification Evidence Extensions (Normative)
- When release target profile is `enterprise` or `regulated`, evidence bundle MUST include:
  - `backend_certification_bundle_hash`,
  - `artifact_store_certification_bundle_hash`,
  - `certification_evidence_bundle_hash` from conformance harness,
  - `observability_mapping_hash` (OTel/Prometheus mapping),
  - `performance_tier_report_hash`,
  - `chaos_recovery_proof_pack_hash` (mandatory in `regulated` mode).
- Bundle completeness failure on any mandatory extension is deterministic fatal.

---
## 3) Initialization
1. Load evidence policy.
2. Resolve required evidence set.
3. Initialize assembly context.

---
## 4) Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Release.CollectEvidenceRefs`
- `Glyphser.Release.BuildEvidenceBundle`
- `Glyphser.Release.ValidateEvidenceBundle`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Release.BuildEvidenceBundle`  
**Signature:** `(evidence_refs, policy -> evidence_bundle)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Builds canonical evidence bundle and computes commitment hash.

---
## 6) Procedure
```text
1. Collect required evidence refs
2. Build canonical evidence bundle
3. Validate completeness and hash links
4. Emit bundle ref and bundle hash
```

---
## 7) Trace & Metrics
- Metrics: `required_evidence_total`, `missing_evidence_count`, `bundle_size_bytes`.
- Trace includes bundle hash and validation status.

---
## 8) Validation
- golden evidence bundles for release profiles.
- deterministic ordering and hash stability tests.

---
## 9) Refactor & Equivalence
- E0 for bundle hash and validation verdict.

---
## 10) Checkpoint/Restore
- checkpoint stores evidence-resolution cursor and partial bundle hash.
- restore continues assembly deterministically.

---
## 11) Related Contracts
- `docs/layer4-implementation/Contracts-Artifact-Lifecycle.md`
- `docs/layer2-specs/Execution-Certificate.md`
- `docs/layer2-specs/Run-Commit-WAL.md`
- `docs/layer3-tests/Game-Day-Scenarios.md`
- `docs/layer4-implementation/Third-Party-Operator-Certification-Program.md`
 - `docs/layer4-implementation/Disaster-Recovery-Operations-Runbook.md`
 - `docs/layer4-implementation/Incident-Postmortem-Template.md`

---
## 12) Evidence Interchange and Recovery Proof Binding (Normative)
- Release evidence MUST be exportable as a portable interchange package:
  - `evidence_bundle.cbor`
  - `evidence_manifest.json`
  - `evidence_signatures/`
  - `verification_instructions.txt`
- Interchange package hash:
  - `evidence_interchange_hash = SHA-256(CBOR_CANONICAL([evidence_bundle_hash, [evidence_manifest_hash, signatures_hash]]))`.
- Third-party verification requirement:
  - package must be verifiable without repository-local state beyond published contract hashes and trust roots.
- Regulated releases MUST embed or reference:
  - `chaos_recovery_proof_pack_hash`,
  - `conformance_coverage_report_hash`,
  - `sbom_hash`,
  - `operator_registry_root_hash`.

## 13) Canonical Artifact Inputs (Normative)
- Canonical contracts and catalogs for doc-phase verifiable assembly:
  - `contracts/operator_registry.cbor`
  - `contracts/digest_catalog.cbor`
  - `contracts/error_codes.cbor`
  - `contracts/capability_catalog.cbor`
  - `contracts/schema_catalog.cbor`
  - `contracts/vectors_catalog.cbor`
  - `contracts/catalog-manifest.json`
- Minimal pinned fixture/evidence inputs:
  - `fixtures/hello-core/fixture-manifest.json`
  - `goldens/hello-core/golden-manifest.json`
  - `vectors/hello-core/vectors-manifest.json`
