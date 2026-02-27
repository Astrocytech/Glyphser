# Glyphser Spec Lint Implementation Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.SpecLint`  
**Purpose (1 sentence):** Define deterministic implementation requirements for cross-document linting and contract-consistency enforcement.  
**Spec Version:** `Glyphser.Implementation.SpecLint` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Contract linting and CI enforcement.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.SpecLint`
- **Purpose (1 sentence):** Deterministic cross-spec lint implementation contract.
### 0.A Objective Semantics
- minimize unresolved contract inconsistencies.
### 0.B Reproducibility Contract
- lint verdict reproducible from `(docs_set_hash, lint_rules_hash, operator_registry_root_hash)`.
### 0.C Numeric Policy
- binary64 only for aggregate lint metrics.
### 0.D Ordering and Tie-Break Policy
- findings ordered by severity, file path, line.
### 0.E Parallel, Concurrency, and Reduction Policy
- checks parallelizable; finding reduction deterministic.
### 0.F Environment and Dependency Policy
- pinned parser/runtime versions required.
### 0.G Operator Manifest
- `Glyphser.Implementation.LoadDocSet`
- `Glyphser.Implementation.RunSpecLintRules`
- `Glyphser.Implementation.AggregateLintVerdict`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- linter entrypoint: `tools/spec_lint.py`.
- normative rule catalog: `docs/layer4-implementation/Spec-Lint-Rules.md`.
### 0.I Outputs and Metric Schema
- outputs: `(lint_report, lint_verdict, lint_metrics)`.
### 0.J Spec Lifecycle Governance
- rule semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- blocker lint findings fail CI deterministically.
### 0.L Input/Data Provenance
- lint run records docs hash and rules hash.

---
## 2) System Model
### I.A Persistent State
- lint ruleset registry.
### I.B Inputs and Hyperparameters
- markdown set, registry artifacts, strictness profile.
### I.C Constraints and Feasible Set
- all referenced contracts must be parseable.
### I.D Transient Variables
- per-rule findings and diagnostics.
### I.E Invariants and Assertions
- no undefined operator or error code references.

---
## 3) Initialization
1. Load lint ruleset and parser profile.
2. Load operator/error registries.
3. Initialize findings collector.

---
## 4) Operator Manifest
- `Glyphser.Implementation.LoadDocSet`
- `Glyphser.Implementation.RunSpecLintRules`
- `Glyphser.Implementation.AggregateLintVerdict`
- `Glyphser.Error.Emit`

---
## 5) Operator Definitions
**Operator:** `Glyphser.Implementation.LoadDocSet`
**Signature:** `(docs_root, include_globs, exclude_globs -> doc_set, doc_set_hash)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Loads documentation corpus under deterministic path ordering and computes stable `doc_set_hash`.

**Operator:** `Glyphser.Implementation.RunSpecLintRules`  
**Signature:** `(doc_set, rule_set -> findings)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Executes rule suite over parsed docs and emits normalized findings.

**Operator:** `Glyphser.Implementation.AggregateLintVerdict`
**Signature:** `(findings -> lint_verdict, lint_metrics)`
**Purity class:** PURE
**Determinism:** deterministic
**Definition:** Reduces normalized findings into deterministic verdict and aggregate metrics using fixed severity precedence.

---
## 6) Procedure
```text
1. Load docs and registries
2. Execute lint rules deterministically
3. Aggregate verdict
4. Fail on blocker-level findings
```

---
## 7) Trace & Metrics
- Metrics: `finding_count`, `blocker_count`, `major_count`, `files_scanned`.
- Trace includes `docs_set_hash`, `rules_hash`, `registry_hashes`.

---
## 8) Validation
- golden lint fixtures (pass/fail) required.
- regression tests for rule determinism and ordering.

---
## 9) Refactor & Equivalence
- E0 for lint verdict and normalized finding list.

---
## 10) Checkpoint/Restore
- checkpoint stores file cursor, rule cursor, findings hash.
- restore must reproduce identical verdict.
