# Glyphser Security Coding Checklist
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Security.CodingChecklist`  
**Purpose (1 sentence):** Define deterministic secure-coding requirements and enforcement checks for implementation and review pipelines.  
**Spec Version:** `Glyphser.Security.CodingChecklist` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Secure implementation governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Security.CodingChecklist`
- **Purpose (1 sentence):** Deterministic secure-coding review contract.
### 0.A Objective Semantics
- minimize exploitable defects and policy violations.
### 0.B Reproducibility Contract
- checklist verdict reproducible from code snapshot + checklist version.
### 0.C Numeric Policy
- binary64 for risk scoring and trend metrics.
### 0.D Ordering and Tie-Break Policy
- findings sorted by severity then path then line.
### 0.E Parallel, Concurrency, and Reduction Policy
- static checks parallelized; finding merge deterministic.
### 0.F Environment and Dependency Policy
- scanner versions and rule packs pinned.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Security.RunStaticSecurityChecks`
- `Glyphser.Security.VerifySecretHandlingRules`
- `Glyphser.Security.VerifyAuthzPathCoverage`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- security governance operators under `Glyphser.Security.*`.
### 0.I Outputs and Metric Schema
- outputs: `(security_findings, security_gate, security_metrics)`.
### 0.J Spec Lifecycle Governance
- mandatory security rule changes are MAJOR.
### 0.K Failure and Error Semantics
- blocker vulnerability findings fail gate deterministically.
### 0.L Input/Data Provenance
- source tree hash, ruleset hash, toolchain hash logged.

---
## 2) System Model
### I.A Persistent State
- security ruleset and suppression registry.
### I.B Inputs and Hyperparameters
- changed files, codebase snapshot, enforcement profile.
### I.C Constraints and Feasible Set
- no undocumented suppression allowed.
### I.D Transient Variables
- per-rule findings.
### I.E Invariants and Assertions
- all authz-critical paths must be covered by checks.

---
## 3) Initialization
1. Load security ruleset.
2. Load source snapshot metadata.
3. Initialize findings sink.

---
## 4) Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Security.RunStaticSecurityChecks`
- `Glyphser.Security.VerifySecretHandlingRules`
- `Glyphser.Security.VerifyAuthzPathCoverage`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Security.VerifySecretHandlingRules`  
**Signature:** `(source_snapshot, ruleset -> findings)`  
**Purity class:** PURE  
**Definition:** Enforces key/secret handling constraints and redaction usage rules.

**Operator:** `Glyphser.Security.VerifyAuthzPathCoverage`  
**Signature:** `(code_map, authz_contract -> coverage_report)`  
**Purity class:** PURE  
**Definition:** Confirms required capability checks exist on protected operator paths.

---
## 6) Procedure
```text
1. run static security checks
2. validate secret handling and redaction policies
3. verify authz-path coverage
4. aggregate findings and gate verdict
5. fail on blocker findings
```

---
## 7) Trace & Metrics
- Metrics: `critical_findings`, `high_findings`, `authz_coverage_pct`, `secret_leak_findings`.
- Trace includes ruleset hash and suppression list hash.

---
## 8) Validation
- golden vulnerable and clean code fixtures.
- deterministic ordering of findings and gate verdict.

---
## 9) Refactor & Equivalence
- E0 for gate verdict and blocker finding identities.

---
## 10) Checkpoint/Restore
- checkpoint stores file cursor, findings hash, and partial verdict state.
- restore resumes scan deterministically.
