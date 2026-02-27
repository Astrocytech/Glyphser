# EQC Ecosystem Master — ML2ML

This is the canonical portfolio master for ML2ML and is normative for portfolio governance, propagation, and validation.
It implements EQC-ES v1.9 requirements as defined in:
`document_guidelines/EquationCode/ECOSYSTEM.md`

## 0.5 Quick Impact Analysis Procedure v1.0
1. Open this file (`ecosystem.md`).
2. Go to Section 5 and identify the change row matching your modification type.
3. Resolve target `DocID` in `ecosystem-registry.yaml` and edges in `ecosystem-graph.yaml`.
4. Apply required actions to every affected document and sidecar.
5. Run:
   - `eqc-es impact --change DOCID@vX.Y.Z`
   - `eqc-es validate`
   - `eqc-es regenerate-sidecars`
6. Record final decision and evidence in `ecosystem-validation-log.md`.

## 1. Identity & Purpose
- Portfolio Name: `ML2ML`
- Purpose: Single source of truth that makes every EQC document discoverable, version-compatible, and automatically updatable.
- Spec Version: `EQC-ES-v1.9` | `2026-02-19` | `ML2ML Team`
- Root Document: `document_guidelines/EquationCode/ECOSYSTEM.md`
- Governance Model: `central-root`

## 2. Document Registry (mandatory)
Authoritative machine-readable registry:
- `ecosystem-registry.yaml`

Every entry must include:
- `DocID`
- `Title`
- `Type`
- `Layer`
- `FilePath` or `GitRef`
- `CurrentVersion` (`vX.Y.Z`)
- `Status`
- `LastUpdated` (`YYYY-MM-DD`)
- `Owner` (optional)
- `SHA256Hash` (with Validation Salt; Section 6)
- `ToolingManifestRef`
- `DataProvenanceRef`
- `PurityClass`
- `DeclaredEdgeTypes`
- `PreviousSHA256` (tamper-evident chain)

Strict Path Resolution (v1.9):
- `eqc-es validate` must confirm each `FilePath/GitRef` is resolvable, file exists, is non-empty, and contains declared version string.

### 2.2 Distributed Governance + Aliasing + State-Isolation + Conflict Escalation
- Each sub-portfolio must carry its own complete EQC-ES master and pass `eqc-es validate`.
- Top-level imports are declared through `ecosystem-imports` in registry.
- Version constraints are AND-composed; empty intersection is invalid.
- Diamond conflicts must resolve by aliasing or strict single-version.
- State-Isolation Check is mandatory: no overlapping writes to persistent state/RNG state unless protected by deterministic reduction.
- Unresolved conflicts escalate to root owner within 24h and must be logged in `ecosystem-validation-log.md` with rationale and equivalence test evidence.

### 2.3 Environment Profiles (mandatory)
Profiles are authoritative in:
- `ecosystem-compatibility-aggregate.yaml`

A document is fully validated only when shadow-traces succeed for every active profile.

Reference profile schema shape:
```yaml
environment_profiles:
  - name: "cpu-x86-64-v3"
    container: "docker.io/myorg/eqc-runtime:2026.02-cpu"
    compiler: "gcc 14.2.0 -O3 -march=x86-64-v3"
    hardware: "x86_64-v3"
    validated_on: "2026-02-19"
```

### 2.4 Layered Architecture (anti-cycle rule)
- Layer 0: core-guidelines; may `IMPORT/EXTEND` only Layer 0.
- Layer 1: operator-library, external-dependency, data-registry; may `IMPORT/EXTEND` Layer 0-1.
- Layer 2: algorithm-spec, checkpoint-schema; may `IMPORT/EXTEND` Layer 0-2.
- Layer 3: test-suite, golden-trace-set; may `IMPORT/EXTEND` Layer 0-3.
- Layer 4+: derived-impl, other; may `IMPORT/EXTEND` Layer 0-4+.

Rule:
- `IMPORT`/`EXTEND` only from layers less than or equal to own layer.
- `RECOGNIZES` may point upward (metadata-only) and is excluded from cycle detection.

Portfolio layout:
- `document_guidelines/`
- `docs/layer1-foundation/`
- `docs/layer2-specs/`
- `docs/layer3-tests/`
- `docs/layer4-implementation/`

### 2.5 Orphan, Shadowing, Ghost Audit
`eqc-es validate` must perform:
- Orphan check
- Shadowing audit
- Ghost-document detection

Policy:
- warning by default
- blocking in strict mode
- experimental docs may remain non-blocking; unresolved findings auto-trigger deprecation proposal after 3 MAJOR portfolio versions.

### 2.6 Data Registry (mandatory for data-driven docs)
Authoritative sidecar:
- `data-registry.yaml`

Data changes trigger propagation with external-dependency semantics (Section 5).

## 3. Dependency Graph (mandatory)
Authoritative sidecar:
- `ecosystem-graph.yaml`

Allowed edge types:
- `IMPORTS`
- `EXTENDS`
- `REFERENCES`
- `PROVIDES`
- `DERIVES`
- `USES`
- `RECOGNIZES`

Rules:
- all docs must declare used edge types in registry
- `RECOGNIZES` is included in reachability/impact analysis and excluded from cycle detection

## 4. Mandatory Compatibility Matrix
Authoritative aggregate:
- `ecosystem-compatibility-aggregate.yaml`

Per-document compatibility entries must include:
- `requires`
- `minimum-equivalence`
- `external_compatibility`

## 5. Change Propagation Protocol (mandatory)

| Change Type | Affected Document Types | Required Actions | Version Impact |
|---|---|---|---|
| EQC-ES MAJOR update | All | Full re-lint, reference updates, Golden Ecosystem Traces | MAJOR |
| EQC-ES MINOR/PATCH update | Direct references | Reference update + targeted validation | MINOR/PATCH |
| Core guideline change | All non-frozen dependents | Re-validate `IMPORT/EXTEND`, migration notes | Propagated by equivalence |
| Operator library version change | All `IMPORT/USE` consumers | Update manifests + compatibility; run E0-E3 where used | MINOR provider, PATCH consumers unless breaking |
| Operator deprecation with replacement | All users | Mark deprecated, apply replacement in grace period | MINOR provider, PATCH consumers |
| Operator removal without replacement | All users | Mandatory migration or usage deletion | MAJOR provider + consumers |
| Trace/metric schema change | Consumers + test suites | Update dependent contracts and tests | MAJOR |
| Test vector / golden trace change | Referencers | Re-run relevant validation suites | PATCH unless breakage |
| Add document | Root + impacted refs | Add registry/graph/data entries; full validation; namespace checks | PATCH unless namespace conflict (MAJOR) |
| External dependency/profile change | Importers | Shadow-traces per active profile; drift report if needed | MAJOR if out of guardrail else MINOR |
| Graph/registry structural change | Root | Full portfolio validation | PATCH unless compatibility break (MAJOR) |

All changes must include:
1. Registry and graph update.
2. Impact analysis output.
3. Validation output.
4. Validation-log record.

Compatibility policy note:
- Legacy Compatibility Shim, Shadow-Trace Requirement + Drift Guardrail, Automated Promotion Path, and portfolio version decision behavior are enforced under this section and Section 8.

## 6. Consistency Invariants (mandatory, lintable)
1. Operator manifests resolve to existing, non-deprecated registry entries.
2. Global semantics are imported or overridden with declared equivalence (E0-E3).
3. Layer constraints hold for all `IMPORT/EXTEND`; upward `RECOGNIZES` stays metadata-only.
4. Total reachability from root over `IMPORT/EXTEND` chains (and metadata reachability checks including `RECOGNIZES`).
5. Hash integrity: each document hash includes direct import target hashes via manifest digest.
6. `RECOGNIZES` edges do not influence functional hashes or operator logic.
7. Every active environment profile has current shadow-traces.
8. No unresolved diamond dependency conflicts.
9. Deprecated operators are not used beyond documented grace periods.
10. `migrating` status is allowed only in open branches.
11. Frozen docs with legacy shims yield warnings unless strict mode elevates.
12. Validation Salt includes minimum-equivalence levels across dependencies.
13. Namespace uniqueness holds across entire portfolio.
14. Orphan/shadowing/ghost/state-isolation checks pass under policy mode.
15. All `other` types declare edge types and purity class.
16. Registry entries include `PreviousSHA256` history chain.
17. Physical Existence Invariant: every registry target resolves and contains declared version string.

## 7. Portfolio Observability & Tooling (mandatory)
Required root sidecars:
- `ecosystem-registry.yaml`
- `ecosystem-graph.yaml`
- `ecosystem-compatibility-aggregate.yaml` (includes Profile Compatibility Aggregate)
- `ecosystem-validation-log.md`
- `data-registry.yaml`
- `migration-plan-template.yaml`
- `portfolio-release-notes-template.md`

Tooling manifest:
- `ecosystem/tooling-manifest.yaml`

Mandatory commands:
- `eqc-es validate` -> JSON: `status`, `errors`, `warnings`, `affected_docs`
- `eqc-es impact --change DOCID@vX.Y.Z` -> JSON: `DocID`, `required_actions`, `version_impact`
- `eqc-es regenerate-sidecars`
- `eqc-es generate-migration-plan`

Formal command output contract:
```yaml
eqc-es validate:
  output:
    status: "pass|fail"
    errors: [string]
    warnings: [string]
    affected_docs: [DocID]
eqc-es impact:
  output:
    impacts:
      - DocID: string
        required_actions: [string]
        version_impact: "PATCH|MINOR|MAJOR"
```

Tooling extensibility requirements:
- Integrate with CI/CD and fail pipeline on non-zero validation errors.
- Enforce linkage with document-level Block VII lint rules.
- Keep tooling-manifest versioned for deterministic evolution.

### 7.5 Self-Validation (Golden Ecosystem Traces)
- Maintain at least one golden ecosystem trace.
- Trace Purity Requirement: shadow-traces must run in Clean-Room state (checkpoint-reset, no cache bleed, deterministic state reset).

## 8. Refactoring & Evolution Rules
- Equivalence tiers: `E0`, `E1`, `E2`, `E3`.
- Hardware tier: `E-HW` with `EPS_HW` per document/profile.
- Portfolio tier: `E-PORT` for graph/registry-level preservation checks.
- Strictest Tolerance Rule: shared operator drift uses minimum `EPS_EQ` across all consumers.
- Tolerance Inheritance: higher-layer docs inherit strictest dependent tolerances for E0/E1 validation.
- Staged transitions use migration plan template and atomic PR workflow.

## 9. Integration with Core EQC Blocks + Portfolio Checkpoint
- Any propagated change must execute relevant document Block VII and, when applicable, Block VIII checks.
- Portfolio checkpoint (extends EQC Block IX) must snapshot:
  - registry
  - dependency graph
  - active environment profiles
  - data registry
  - validation/log state
- Atomic Checkpoint Hash must include hash of this `ecosystem.md` and governing `document_guidelines/EquationCode/ECOSYSTEM.md`.

## 10. Governance & Lifecycle
Required flow:
1. Branch.
2. Edit documents and sidecars.
3. Run impact analysis.
4. Run full validation.
5. Apply required updates on all affected docs.
6. Merge atomically and append validation log.

Lifecycle rules:
- Deprecations must remain readable for at least one full MAJOR portfolio version with documented grace period.
- Backward-compatibility shims required for frozen docs where applicable.
- Release notes must include impacts, equivalence outcomes, drift reports, and profile compatibility state.
- Localization Policy: registry may declare supported languages; all core sections keep English master with optional translations.
- Portfolio version rule decision tree is governed by Section 5 version impact with most-severe outcome prevailing.

## 11. Glossary
- Shadow-trace: Golden trace replay after change to evaluate equivalence.
- Drift Report: Signed rationale for metric movement inside allowed tolerance.
- Diamond dependency: Conflicting version requirements on the same provider.
- Validation Salt: Hash input tying dependency equivalence levels to integrity.
- E-PORT: Portfolio-wide equivalence level.
- Hardware-locked: Profile-bound behavior unable to satisfy cross-profile tolerance.
- Clean-Room state: fully reset deterministic execution state for validation traces.
