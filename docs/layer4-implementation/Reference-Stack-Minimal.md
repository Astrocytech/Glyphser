# Glyphser Minimal Runnable Reference Stack
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.ReferenceStack.Minimal`  
**Purpose (1 sentence):** Define a minimal runnable reference implementation that proves the full deterministic lifecycle from manifest to certificate and replay.  
**Spec Version:** `Glyphser.ReferenceStack.Minimal` | 2026-02-20 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Executable reference implementation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.ReferenceStack.Minimal`
- **Purpose (1 sentence):** End-to-end runnable proof of contract interoperability.
### 0.A Objective Semantics
- Execute the smallest useful pipeline that demonstrates deterministic lifecycle closure.
### 0.B Reproducibility Contract
- Replayable given `(manifest_hash, env_manifest_hash, replay_token, operator_registry_root_hash, fixture_hash)`.
### 0.C Numeric Policy
- IEEE-754 binary64, round-to-nearest ties-to-even.
### 0.D Ordering and Tie-Break Policy
- Single-worker deterministic ordering by step index.
### 0.E Parallel, Concurrency, and Reduction Policy
- No parallel execution in minimal stack.
### 0.F Environment and Dependency Policy
- Locked dependency manifest required.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Config.NormalizeDefaults`
- `Glyphser.Data.NextBatch`
- `Glyphser.Model.ModelIR_Executor`
- `Glyphser.Trace.ComputeTraceHash`
- `Glyphser.Checkpoint.Write`
- `Glyphser.Certificate.Build`
- `Glyphser.Replay.CompareTrace`
### 0.H Namespacing and Packaging
- Reference stack package path: `reference/minimal_stack/`.
### 0.I Outputs and Metric Schema
- Outputs: `(run_report, trace_final_hash, checkpoint_hash, certificate_hash, replay_verdict)`.
### 0.J Spec Lifecycle Governance
- Breaking lifecycle changes require MAJOR bump.
### 0.K Failure and Error Semantics
- Deterministic abort on first contract violation.
### 0.L Input/Data Provenance
- Fixture dataset, model IR, and manifest must be content-addressed.

---
## 2) System Model
### I.A Persistent State
- Minimal run state: manifest, RNG offsets, model params, trace chain state.
### I.B Inputs and Hyperparameters
- tiny synthetic dataset, tiny linear model IR, fixed seed.
### I.C Constraints and Feasible Set
- Single-node local mode only.
### I.D Transient Variables
- per-step batch, logits/loss, gradients, trace events.
### I.E Invariants and Assertions
- Same inputs produce same trace/certificate hashes.

---
## 3) Procedure
```text
1. Load canonical manifest + fixtures.
2. Normalize config defaults and derive replay_token.
3. For each train step: NextBatch -> ModelIR_Executor.
4. Emit trace records and compute trace_final_hash.
5. Write checkpoint and compute checkpoint_hash.
6. Build execution certificate and compute certificate_hash.
7. Replay same run and compare trace with Replay.CompareTrace.
8. Emit run_report and replay_verdict.
```

---
## 4) Validation
- Required deliverable: runnable script that reproduces identical lifecycle hashes on every supported host profile.
- Required artifacts:
  - `fixtures/hello-core/manifest.core.yaml`
  - `fixtures/hello-core/model_ir.json`
  - `fixtures/hello-core/tiny_synth_dataset.jsonl`
  - `goldens/hello-core/trace_snippet.json`
  - `goldens/hello-core/checkpoint_header.json`
  - `goldens/hello-core/execution_certificate.json`
  - `contracts/operator_registry.cbor`
  - `contracts/catalog-manifest.json`
  - `vectors/hello-core/vectors.json`
  - `vectors/hello-core/vectors-manifest.json`

## 4.A Artifact Identity Verification (Normative)
- Before claiming runnable-reference conformance, run:
  - `python tools/verify_doc_artifacts.py`
- Hash identities used by this contract are the values in:
  - `contracts/catalog-manifest.json`
  - `fixtures/hello-core/fixture-manifest.json`
  - `goldens/hello-core/golden-manifest.json`

---
## 5) Related Contracts
- `docs/layer2-specs/Glyphser-Kernel-v3.22-OS.md`
- `docs/layer2-specs/ModelIR-Executor.md`
- `docs/layer2-specs/Execution-Certificate.md`
- `docs/layer2-specs/Replay-Determinism.md`

---
## 6) Procedure
```text
1. Read and apply this document together with its referenced normative contracts.
2. Preserve deterministic ordering and evidence linkage requirements declared by those contracts.
3. Emit deterministic documentation compliance record for governance tracking.
```
