# Glyphser Spec Lint Rules Catalog
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Implementation.SpecLintRules`
**Purpose (1 sentence):** Define the normative lint-rule catalog and severities for deterministic cross-document contract validation.
**Spec Version:** `Glyphser.Implementation.SpecLintRules` | 2026-02-19 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Lint rules governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Implementation.SpecLintRules`
- **Purpose (1 sentence):** Deterministic rule catalog for `tools/spec_lint.py`.
### 0.A Objective Semantics
- Maximize contract coherence and eliminate silent cross-file drift.
### 0.B Reproducibility Contract
- Rule verdicts replayable from `(docs_set_hash, rules_catalog_hash, registry_hashes)`.
### 0.C Numeric Policy
- binary64 for aggregate statistics only.
### 0.D Ordering and Tie-Break Policy
- findings ordered by `(severity desc, doc_path asc, line asc, rule_id asc)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- rules may run in parallel; merged findings must preserve deterministic ordering.
### 0.F Environment and Dependency Policy
- parser and regex engine versions pinned in tooling manifest.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `Glyphser.Implementation.SpecLint`
- `Glyphser.Implementation.LoadRuleCatalog`
- `Glyphser.Implementation.EvaluateRuleSet`
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- Rule catalog source path: `docs/layer4-implementation/Spec-Lint-Rules.md`.
### 0.I Outputs and Metric Schema
- outputs: `(findings, verdict, lint_metrics)`.
### 0.J Spec Lifecycle Governance
- New BLOCKER rules are MINOR; changed rule semantics are MAJOR.
### 0.K Failure and Error Semantics
- BLOCKER findings fail validation deterministically.
### 0.L Input/Data Provenance
- lint run stores docs hash and catalog hash in trace metadata.

---
## 2) Normative Rule Set
| Rule ID | Severity | Description | Failure Code |
|---|---|---|---|
| `EQC.LINK.RESOLVE` | BLOCKER | Every project-local `.md` reference must resolve. | `CONTRACT_VIOLATION` |
| `EQC.GRAPH.PARITY` | BLOCKER | Every discovered doc reference must have an edge in `ecosystem-graph.yaml`. | `CONTRACT_VIOLATION` |
| `EQC.GRAPH.STALE_EDGE` | BLOCKER | `REFERENCES` edges must correspond to real references in source docs. | `CONTRACT_VIOLATION` |
| `EQC.REG.PATH.EXISTS` | BLOCKER | Every `FilePath` in registry must exist and be non-empty. | `CONTRACT_VIOLATION` |
| `EQC.REG.VERSION.MATCH` | BLOCKER | Registry version declaration must match file-declared version token policy. | `CONTRACT_VIOLATION` |
| `EQC.EDGE.DECLARED` | BLOCKER | Graph edge types must be declared in source doc `DeclaredEdgeTypes`. | `CONTRACT_VIOLATION` |
| `EQC.LAYER.IMPORTS` | BLOCKER | `IMPORTS/EXTENDS` must not target higher layer. | `CONTRACT_VIOLATION` |
| `EQC.HASH.COMMIT.SHAPE` | BLOCKER | Any hash declared as signature/commitment and written as `SHA-256(CBOR_CANONICAL([...]))` MUST have an outer 2-element array `[domain_tag, data_object]` (no flattening). | `CONTRACT_VIOLATION` |
| `OP_MANIFEST_UNRESOLVED_SYMBOL` | BLOCKER | Any backticked `Glyphser.*_vN` listed under an Operator Manifest/Referenced Operators section must resolve to exactly one `**Operator:**` definition in the doc set, unless explicitly declared as `External operator reference: <op> is defined in <doc>`. | `CONTRACT_VIOLATION` |
| `EQC.GRAPH.REACHABLE` | MAJOR | All docs must be reachable from `CORE-MASTER-001` via metadata/governance edges. | `CONTRACT_VIOLATION` |
| `EQC.DOCID.UNIQUE` | BLOCKER | Registry `DocID` values must be unique. | `CONTRACT_VIOLATION` |
| `EQC.FILEPATH.UNIQUE` | BLOCKER | Registry `FilePath` values must be unique. | `CONTRACT_VIOLATION` |

---
## 3) Rule Evaluation Procedure
```text
1. Parse registry + graph + markdown corpus
2. Resolve references and build discovered ref set
3. Run blocker rules first
4. Run MAJOR/MINOR informational rules
5. Emit deterministic finding stream and verdict
```

---
## 4) Wiring References
- `docs/layer4-implementation/Spec-Lint-Implementation.md`
- `docs/layer4-implementation/Repo-Layout-and-Interfaces.md`
- `ecosystem.md`
- `ecosystem-registry.yaml`
- `ecosystem-graph.yaml`

---
## 6) Procedure
```text
1. Read and apply this document together with its referenced normative contracts.
2. Preserve deterministic ordering and evidence linkage requirements declared by those contracts.
3. Emit deterministic documentation compliance record for governance tracking.
```
