# Glyphser Normativity Legend
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `Glyphser.Governance.NormativityLegend`  
**Purpose (1 sentence):** Define normative interpretation tags used across Glyphser contracts.  
**Spec Version:** `Glyphser.Governance.NormativityLegend` | 2026-02-21 | Authors: Olejar Damir  
**Domain / Problem Class:** Contract interpretation and governance clarity.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `Glyphser.Governance.NormativityLegend`
- **Purpose (1 sentence):** Canonical normativity legend.
### 0.A Objective Semantics
- Remove interpretation ambiguity between enforceable protocol rules and explanatory text.
### 0.B Reproducibility Contract
- Replayable given `(legend_version, tagged_sections)`.
### 0.C Numeric Policy
- N/A.
### 0.D Ordering and Tie-Break Policy
- N/A.
### 0.E Parallel, Concurrency, and Reduction Policy
- N/A.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for interpretation of tags.
### 0.G Operator Manifest
- `Glyphser.Error.Emit`
### 0.H Namespacing and Packaging
- This legend applies across all contracts under `docs/`.
### 0.I Outputs and Metric Schema
- Outputs: `(normativity_interpretation_report)`.
### 0.J Spec Lifecycle Governance
- Tag definitions are MAJOR-governed.
### 0.K Failure and Error Semantics
- Mis-tagged required sections are deterministic lint failures.
### 0.L Input/Data Provenance
- Inputs are contract sections and heading metadata.

### 0.Z EQC Mandatory Declarations Addendum
- `stochastic_used: false`
- `seed_space: N/A`
- `prng_family: N/A`
- `rng_ownership: N/A`
- `numeric_kernel: N/A`
- `tolerances: N/A`
- `determinism_level: BITWISE`
- `error_trace: inherited from docs/layer1-foundation/Error-Codes.md`

---
## 2) Normativity Tags (Normative)
- `Normative`:
  - Enforceable requirements with conformance impact.
  - Violations are deterministic failures for compliant implementations.
- `Informative`:
  - Explanatory guidance and examples.
  - Does not modify conformance requirements.
- `Template-only`:
  - Structural EQC completeness content with no runtime/protocol semantics.
  - Must not be interpreted as execution behavior requirements.

---
## 3) Required Usage Rule
- Every contract SHOULD mark section headings with one of:
  - `(Normative)`
  - `(Informative)`
  - `(Template-only)`
- If a section is untagged, interpretation defaults to:
  - sections `0.*`, `II.*`, `4)`, `5)`, `6)`: `Normative`
  - examples/tutorial walkthroughs: `Informative`
  - structural compliance placeholders: `Template-only`

## 6) Procedure
```text
1. Read target contract section.
2. Resolve explicit tag if present.
3. If absent, apply default mapping rule from Section 3.
4. Emit deterministic interpretation record for lint/audit tooling.
```
