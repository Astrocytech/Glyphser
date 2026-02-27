# Glyphser PR Review Checklist
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.PRReviewChecklist`  
**Purpose (1 sentence):** Define deterministic pull-request review gates for contract safety, replay integrity, and regression risk control.  
**Spec Version:** `Glyphser.Implementation.PRReviewChecklist` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Engineering governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.PRReviewChecklist`
- **Purpose (1 sentence):** Deterministic PR quality gating checklist.
### 0.A Objective Semantics
- minimize unresolved high-severity findings.
### 0.B Reproducibility Contract
- review verdict reproducible from changed files + checklist version.
### 0.C Numeric Policy
- binary64 for computed risk scores.
### 0.D Ordering and Tie-Break Policy
- findings sorted by severity then file path then line.
### 0.E Parallel, Concurrency, and Reduction Policy
- independent checks may run in parallel; reductions deterministic.
### 0.F Environment and Dependency Policy
- checklist toolchain pinned by lockfile.
### 0.G Operator Manifest
- `Glyphser.Implementation.ScanChangedContracts`
- `Glyphser.Implementation.ScorePRRisk`
- `Glyphser.Implementation.DecideReviewGate`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- operators under `Glyphser.Implementation.*`.
### 0.I Outputs and Metric Schema
- `(review_findings, review_gate, review_metrics)`.
### 0.J Spec Lifecycle Governance
- gate criteria changes are MAJOR.
### 0.K Failure and Error Semantics
- unresolved blocker findings force deterministic failure.
### 0.L Input/Data Provenance
- uses git diff, registry hash, test outputs.

---
## 2) System Model
### I.A Persistent State
- checklist version, ruleset hash.
### I.B Inputs and Hyperparameters
- changed files, changed operators, CI evidence bundle.
### I.C Constraints and Feasible Set
- PR must include evidence for changed contract-critical docs/code.
### I.D Transient Variables
- per-check findings.
### I.E Invariants and Assertions
- no merge on blocker-level findings.

---
## 3) Initialization
1. Load ruleset.
2. Load changed file manifest.
3. Initialize findings container.

---
## 4) Operator Manifest
- `Glyphser.Implementation.ScanChangedContracts`
- `Glyphser.Implementation.ScorePRRisk`
- `Glyphser.Implementation.DecideReviewGate`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Implementation.ScanChangedContracts`  
**Signature:** `(changed_files, ruleset -> findings)`  
**Purity class:** PURE  
**Definition:** Detects contract-impacting changes and missing updates.

**Operator:** `Glyphser.Implementation.ScorePRRisk`
**Signature:** `(findings, evidence_bundle -> risk_score, review_metrics)`
**Purity class:** PURE
**Definition:** Computes deterministic risk score and review metrics from findings and attached evidence.

**Operator:** `Glyphser.Implementation.DecideReviewGate`  
**Signature:** `(findings, risk_score -> gate_verdict)`  
**Purity class:** PURE  
**Definition:** Produces `PASS/WARN/FAIL` deterministically.

---
## 6) Procedure
```text
1. findings <- ScanChangedContracts(...)
2. risk <- ScorePRRisk(findings)
3. gate <- DecideReviewGate(findings, risk)
4. if gate == FAIL: Error.Emit(CONTRACT_VIOLATION)
5. return (review_findings, review_gate, review_metrics)
```

---
## 7) Trace & Metrics
- Metrics: `blocker_count`, `major_count`, `coverage_delta`, `risk_score`.
- Trace includes checklist version and rule hash.

---
## 8) Validation
- Golden PR examples for pass/warn/fail.
- Regression test for deterministic finding ordering.

---
## 9) Refactor & Equivalence
- E0 for gate verdict and finding ordering.
- E1 allowed for non-gating timing metrics only.

---
## 10) Checkpoint/Restore
- Review checkpoint stores findings and gate snapshot.
- Restore reproduces exact verdict.
