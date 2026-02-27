# Glyphser SRE Incident Triage Playbook
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Operations.SREIncidentTriage`  
**Purpose (1 sentence):** Define deterministic incident triage and remediation workflow for runtime, replay, storage, and governance failures.  
**Spec Version:** `Glyphser.Operations.SREIncidentTriage` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Production reliability operations.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Operations.SREIncidentTriage`
- **Purpose (1 sentence):** Deterministic incident triage and escalation contract.
### 0.A Objective Semantics
- minimize MTTR while preserving evidence integrity.
### 0.B Reproducibility Contract
- triage outcome reproducible from incident evidence bundle hash.
### 0.C Numeric Policy
- binary64 for SLO impact and timing metrics.
### 0.D Ordering and Tie-Break Policy
- triage order fixed by severity then detector timestamp.
### 0.E Parallel, Concurrency, and Reduction Policy
- independent incident checks parallelizable; verdict merge deterministic.
### 0.F Environment and Dependency Policy
- incident analysis uses frozen evidence artifacts only.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Operations.ClassifyIncident`
- `Glyphser.Operations.RunTriageChecklist`
- `Glyphser.Operations.EmitRemediationPlan`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- `Glyphser.Operations.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(incident_report, triage_verdict, remediation_plan)`.
### 0.J Spec Lifecycle Governance
- severity model changes are MAJOR.
### 0.K Failure and Error Semantics
- missing mandatory evidence is a fatal triage failure.
### 0.L Input/Data Provenance
- incident evidence must include trace/checkpoint/WAL/certificate references.

---
## 2) System Model
### I.A Persistent State
- incident catalog and remediation runbooks.
### I.B Inputs and Hyperparameters
- incident id, evidence bundle refs, triage profile.
### I.C Constraints and Feasible Set
- triage cannot proceed without evidence integrity verification.
### I.D Transient Variables
- per-check findings and severity updates.
### I.E Invariants and Assertions
- every incident ends in deterministic terminal state.

---
## 3) Initialization
1. Load incident profile and severity matrix.
2. Load evidence bundle.
3. Initialize triage context.

---
## 4) Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Operations.ClassifyIncident`
- `Glyphser.Operations.RunTriageChecklist`
- `Glyphser.Operations.EmitRemediationPlan`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Operations.RunTriageChecklist`  
**Signature:** `(incident_class, evidence -> triage_findings)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Executes incident-class-specific deterministic checks and returns findings.

---
## 6) Procedure
```text
1. Classify incident
2. Run deterministic triage checklist
3. Emit remediation plan with ordered actions
4. Record terminal triage verdict
```

---
## 7) Trace & Metrics
- Metrics: `incidents_by_severity`, `mttr_minutes`, `evidence_integrity_failures`.
- Trace includes incident class, checklist id, and remediation plan hash.

---
## 8) Validation
- incident replay fixtures for WAL corruption, replay divergence, checkpoint mismatch, certificate mismatch.
- deterministic triage ordering tests.

---
## 9) Refactor & Equivalence
- E0 for incident class and remediation action order.

---
## 10) Checkpoint/Restore
- triage checkpoint stores completed checklist steps and findings hash.
- restore continues deterministically from next step.
