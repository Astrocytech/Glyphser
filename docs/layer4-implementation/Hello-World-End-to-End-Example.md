# Glyphser Hello World End-to-End Example
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.ReferenceExample.HelloWorld`  
**Purpose (1 sentence):** Provide a full, concrete worked example from manifest to final certificate for a tiny model.  
**Spec Version:** `Glyphser.ReferenceExample.HelloWorld` | 2026-02-20 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Integrated tutorial-grade deterministic workflow.

---
## 1) Example Inputs (Normative)
- Manifest: minimal local profile with fixed `tenant_id`, `seed`, `datasets`, and `policy_bundle`.
- Model IR: single linear layer + MSE loss.
- Data: synthetic fixed-size fixture set.
- Steps: exactly 3 train steps.

## 2) Expected Workflow Outputs
- Canonical manifest hash.
- Deterministic per-step trace records.
- Checkpoint header hash and checkpoint hash.
- Execution certificate hash.
- Replay comparison verdict (`E0` pass).

## 3) Output Bundle Structure
- `hello_world/manifest.yaml`
- `hello_world/model_ir.json`
- `hello_world/trace_sidecar.cborlog`
- `hello_world/checkpoint_header.cbor`
- `hello_world/execution_certificate.cbor`
- `hello_world/replay_report.json`

## 4) Acceptance Criteria
- Byte-identical `trace_final_hash` across reruns.
- Byte-identical `certificate_hash` across reruns.
- Replay comparator returns no divergences.

## 5) Related Contracts
- `docs/layer4-implementation/Reference-Stack-Minimal.md`
- `docs/layer3-tests/Test-Plan.md`
- `docs/layer2-specs/Trace-Sidecar.md`

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Structural.Addendum`
- **Purpose (1 sentence):** Structural EQC compliance addendum for "Glyphser Hello World End-to-End Example" without altering existing semantics.
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
