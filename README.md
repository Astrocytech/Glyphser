# Glyphser

Company: **Astrocytech**

Official Astrocytech website: https://www.astrocytech.com

GitHub: https://github.com/Astrocytech/Glyphser

Core purpose: Glyphser exists to make ML and data workflow results repeatable and verifiable. It helps teams prove that the same inputs produce the same outcomes, with evidence they can audit and trust.

Glyphser is a deterministic execution and verification platform for ML workflows. In plain terms, it helps teams run the same workload repeatedly and prove that the result is consistent by producing verifiable evidence files (hashes, conformance outputs, and release checks).

## What This Software Is
- A Python-based runtime and tooling stack focused on reproducibility and verification.
- A repository that combines executable runtime code, formal specs, test suites, and evidence artifacts.
- A self-hosted project track for operators, platform teams, and compliance-focused engineering workflows.

## What It Does
- Runs deterministic validation pipelines over known fixtures and profiles.
- Produces machine-checkable evidence such as trace hashes, certificate artifacts, and conformance reports.
- Verifies release integrity using published checksums.
- Provides policy and spec material for auditability, governance, and compatibility review.

## Why It Exists
ML and data systems can drift across environments, dependencies, and runtime stacks. Glyphser exists to reduce ambiguity by making runs reproducible and by attaching cryptographic-style evidence to the outcome so teams can inspect, compare, and audit what happened.

## How It Works (Simple View)
1. You run a workload or fixture through a declared profile.
2. Glyphser executes deterministic runtime steps (including trace, checkpoint, and certificate flows).
3. It computes stable identifiers and evidence outputs from canonicalized artifacts.
4. Gates and conformance tooling validate structure, contracts, and expected outcomes.
5. You receive PASS/FAIL outputs plus evidence files that can be checked later.

## Who It Is For
- Platform engineers integrating deterministic verification into CI/CD.
- ML systems engineers validating replay and execution evidence.
- Security/compliance reviewers who need release and chain-of-custody checks.

## Quick Start
1. Use Python 3.12+.
2. Install dependencies:
   ```bash
   python -m pip install -e .
   ```
3. Run local release verification:
   ```bash
   python tooling/release/verify_release.py
   ```
4. For the full pipeline directly:
   ```bash
   python tooling/commands/push_button.py
   ```

## ML Training Example
Glyphser includes a small deterministic training fixture (tiny linear regression) you can inspect and run:
- Training manifest: `artifacts/inputs/fixtures/hello-core/manifest.core.yaml`
- Model IR: `artifacts/inputs/fixtures/hello-core/model_ir.json`
- Example walkthrough: `specs/layers/L4-implementation/Hello-World-End-to-End-Example.md`

Run the end-to-end verification flow:
```bash
python tooling/release/verify_release.py
```

Run the full project pipeline directly:
```bash
python tooling/commands/push_button.py
```

## What You Should Expect After Running
- Deterministic gate and conformance checks.
- Generated evidence under `evidence/`.
- Release checksum verification against `distribution/release/CHECKSUMS_v0.1.0.sha256`.
- A final `VERIFY_RELEASE: PASS` when all required checks succeed.

## Project Guide: What Each Region Means
This repository is organized so you can quickly tell where behavior is defined, where it is implemented, how it is tested, and where proof of results is stored.

### Runtime (`runtime/`)
This is the executable Python code behind Glyphser. It is where deterministic execution, tracing, checkpointing, APIs, and CLI behavior are implemented. If you want to understand what actually runs, start here.

### Specifications (`specs/`)
These are the written technical contracts that describe expected system behavior. Think of this area as the source of truth for how Glyphser is supposed to work.

### Schemas (`specs/schemas/`)
These are machine-readable schema files used to validate structure and compatibility. They help keep configs and artifacts consistent across tools and environments.

### Tests (`tests/`)
This area contains unit, integration, gate, replay, and fuzz tests. Its purpose is to prove that implementation still matches expected behavior and to catch regressions early.

### Artifacts (`artifacts/`)
This contains deterministic fixtures, known-good outputs, generated bundles, and input vectors. Use it when you need reproducible inputs and expected results for repeatable verification.

### Evidence (`evidence/`)
This is where generated reports and verification outputs are stored. It represents the project’s audit trail: what checks were run, what passed or failed, and what proof was produced.

### Tooling (`tooling/`)
This area provides automation scripts for validation gates, conformance, code generation, deployment flows, and release tasks. It is the standard way to run the project reliably without ad-hoc command chains.

### Distribution (`distribution/`)
This region contains release-facing assets such as checksums, signatures, and release notes. It exists so users can verify integrity and trust what they download.

### Documentation (`docs/`)
This is the onboarding and navigation layer for contributors and operators. If you are new to the repository, start here for practical guidance.

### Product Materials (`product/`)
This includes product-facing guides, policies, runbooks, and milestone reports. It explains operational expectations and how Glyphser is positioned for real-world usage.

### Governance (`governance/`)
This contains roadmap files, structural policies, and process controls. It explains how the repository is managed and why it is organized the way it is.

### CI Workflows (`.github/workflows/`)
These files define automated checks run in CI. They show what quality and conformance gates are enforced during pull requests and release flows.

### Root-Level Files
Top-level files such as `README.md`, `pyproject.toml`, `LICENSE`, and release policy docs define setup requirements, package metadata, and legal/project-wide context.

## Key Documents
- Start here: `docs/START-HERE.md`
- Verify locally: `docs/VERIFY.md`
- Product scope: `product/handbook/guides/PRODUCT_SCOPE.md`
- Spec layer overview: `specs/README.md`

## Technical Claims Draft
1. A deterministic ML workflow verification system comprising:
   - a runtime that executes declared workload fixtures under profile constraints,
   - a canonical artifact processing path that computes stable evidence identities,
   - and a validation pipeline that emits conformance and release-verification outcomes.
2. The system of claim 1, wherein deterministic evidence identities include at least one trace-derived hash, one certificate-related artifact identity, and one interface or contract-bound identity.
3. The system of claim 1, wherein verification includes checksum comparison of release artifacts against a published checksum manifest.
4. The system of claim 1, wherein execution results are recorded as reproducibility evidence under a dedicated evidence directory for later audit and replay comparison.
5. The system of claim 1, wherein profile-scoped policies define supported environments, operational constraints, and admissible claim boundaries.
6. The system of claim 1, wherein gates validate structural, schema, contract, and observability requirements before a release verification pass condition is reported.
7. A method for reproducible ML execution assurance comprising:
   - receiving a declared workload manifest and profile,
   - executing deterministic runtime stages including trace and checkpoint flows,
   - generating canonicalized evidence artifacts,
   - and outputting a pass/fail verification result linked to generated evidence.
8. The method of claim 7, wherein the pass condition requires successful pipeline execution and successful verification of expected release artifact hashes.

## Claim Boundaries
- Claims in this repository are scoped to documented profiles, fixtures, gates, and evidence included here.
- Environment universality, certifications, or external compliance guarantees are only valid where explicitly documented.
- No external affiliation or certification should be inferred unless it is explicitly stated in project materials.

## License
GNU AGPL v3.0. See `LICENSE`.
