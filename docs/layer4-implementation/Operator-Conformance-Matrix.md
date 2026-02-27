# Glyphser Operator Conformance Matrix
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.OperatorConformanceMatrix`  
**Purpose (1 sentence):** Define deterministic operator implementation and conformance tracking for coding progress and release gating.  
**Spec Version:** `Glyphser.Implementation.OperatorConformanceMatrix` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Implementation governance and conformance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.OperatorConformanceMatrix`
- **Purpose (1 sentence):** Canonical operator conformance tracking contract.
### 0.A Objective Semantics
- optimize for maximal conformance coverage with minimal unresolved blockers.
### 0.B Reproducibility Contract
- conformance verdict reproducible from registry hash + evidence hashes.
### 0.C Numeric Policy
- binary64 only for summary metrics.
### 0.D Ordering and Tie-Break Policy
- rows ordered by `operator_id` lexical ascending.
### 0.E Parallel, Concurrency, and Reduction Policy
- operator checks may run in parallel; merged deterministically.
### 0.F Environment and Dependency Policy
- conformance checks run under lockfile-pinned toolchain.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Implementation.LoadOperatorRegistry`
- `Glyphser.Implementation.ResolveOperatorEvidence`
- `Glyphser.Implementation.ScoreOperatorConformance`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- implementation governance operators under `Glyphser.Implementation.*`.
### 0.I Outputs and Metric Schema
- outputs: `(conformance_matrix, conformance_summary, blockers)`.
### 0.J Spec Lifecycle Governance
- scoring rubric changes are MAJOR.
### 0.K Failure and Error Semantics
- unresolved mandatory evidence emits deterministic failure.
### 0.L Input/Data Provenance
- consumes registry artifact, test manifests, trace/certificate references.

---
## 2) System Model
### I.A Persistent State
- conformance matrix state keyed by `operator_id`.
### I.B Inputs and Hyperparameters
- operator registry, code map, test map, evidence map.
### I.C Constraints and Feasible Set
- each operator must map to exactly one implementation owner.
### I.D Transient Variables
- per-operator status and scoring details.
### I.E Invariants and Assertions
- no duplicate operator ids.

---
## 3) Initialization
1. Load operator registry.
2. Load implementation/test/evidence indexes.
3. Initialize conformance accumulator.

---
## 4) Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Implementation.LoadOperatorRegistry`
- `Glyphser.Implementation.ResolveOperatorEvidence`
- `Glyphser.Implementation.ScoreOperatorConformance`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Implementation.ResolveOperatorEvidence`  
**Signature:** `(operator_id, evidence_indexes -> evidence_row)`  
**Purity class:** PURE  
**Definition:** Resolves implementation path, tests, vectors, and trace evidence for operator.

**Operator:** `Glyphser.Implementation.ScoreOperatorConformance`  
**Signature:** `(evidence_row -> conformance_status, score)`  
**Purity class:** PURE  
**Definition:** Produces deterministic status in `{STUB, PARTIAL, COMPLETE, CERTIFIED}`.

---
## 6) Procedure
```text
1. registry <- LoadOperatorRegistry(...)
2. for operator_id in sorted(registry):
     evidence_row <- ResolveOperatorEvidence(...)
     status <- ScoreOperatorConformance(evidence_row)
3. aggregate summary metrics
4. fail if required operators not COMPLETE+ for target gate
```

---
## 7) Trace & Metrics
- Metrics: `coverage_pct`, `stub_count`, `partial_count`, `complete_count`, `certified_count`.
- Trace fields: `operator_id`, `status`, `missing_evidence_codes`.

---
## 8) Validation
- Golden conformance matrix snapshots.
- Deterministic sorting and scoring vector checks.

---
## 9) Refactor & Equivalence
- E0 for matrix rows and statuses.
- E1 for non-gating timing counters only.

---
## 10) Checkpoint/Restore
- checkpoint stores processed operator cursor + partial summary.
- restore resumes and yields identical final matrix.

---
## 11) Profile Threshold Policy (Normative)
- Conformance matrix MUST classify each operator as:
  - `required_core`, `required_enterprise`, `required_regulated`, or `optional`.
- Coverage thresholds are enforced by profile:
  - `core`: at most 5% optional gaps; no required-core blockers.
  - `enterprise`: at most 2% optional gaps; no required-enterprise blockers.
  - `regulated`: no gaps in required-regulated set.
- Output contract extension:
  - `conformance_summary` MUST include `coverage_pct_by_profile` and `blockers_by_profile`.
- External certification label mapping:
  - operators/modules with `CERTIFIED` status and zero blockers in target profile MAY be labeled `Glyphser Certified Module`.
