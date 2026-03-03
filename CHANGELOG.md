# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added
- `glyphser run --example hello` quick-start command alias.
- Proof demo script with same-seed parity and changed-seed divergence evidence.
- External validation pack and CI gate template docs.
- Quickstart notebook and pipeline tutorial docs.
- Alternatives and use-cases docs for evaluation context.
- Getting-started guide, CI snippets (GitHub/GitLab/Jenkins), and architecture/evidence diagrams doc.
- Scikit-learn and TensorFlow reproducibility example scripts.
- Variance impact benchmark script and benchmark impact documentation.
- Public roadmap and PR template.
- Mypy type-check gate in CI and `mypy.ini` project config.
- Docker quickstart docs and Dockerfile default deterministic demo command.
- MLflow integration example script and starter issue backlog doc.
- Spec-implementation congruence gate and traceability index generation.
- Property-style determinism invariants tests for stable digest behavior.
- Spec-to-implementation required test linkage matrix (`docs/SPEC_IMPLEMENTATION_MATRIX.md`).
- Per-module coverage gate for critical paths (`glyphser/public`, `tooling/release`, `tooling/quality_gates`).
- Canonical evidence metadata schema/catalog generation and validation gate.
- Day-1 contributor pathway rewrite in `docs/START-HERE.md`.
- Developer bootstrap command (`tooling/commands/bootstrap_dev.py`).
- Ruff lint/format enforcement in CI (`ruff check`, `ruff format --check`).
- Cross-platform determinism matrix CI job (`determinism-matrix`).
- API deprecation compatibility aliases with warning tests.
- Schema evolution compatibility gate for legacy evidence metadata fixtures.
- Evidence archive/retention automation and lifecycle documentation.

## [0.2.0] - 2026-03-03

### Added
- One-command deterministic fixture verification: `glyphser verify hello-core`.
- Navigation-first docs set: glossary, evidence formats, integrations, and independent verification guides.
- CI workflow with Linux/macOS and Python 3.11/3.12 matrix.
- Coverage artifact upload (XML + HTML) in CI.
- Release workflow hardening with release checksums, SBOM, and provenance artifacts.

## [0.1.0] - 2026-03-03

### Added
- Stable public package boundary under `glyphser.public`.
- Top-level stable re-exports in `glyphser.__init__`.
- Installable package metadata and `glyphser` CLI script entrypoint.
- User-facing CLI commands: `glyphser verify` and `glyphser snapshot`.
- 5-minute quickstart in README.
- Architecture, compatibility matrix, and deprecation policy docs.
- Release process doc and tag-based release workflow.
- Auto-generated API reference tooling and generated docs.
- Issue templates for bug reports and feature requests.
- Real PyTorch integration example for deterministic digest verification.
- Benchmark harness and benchmark evidence output.

### Changed
- Repository onboarding is now experience-first while keeping spec-first depth available.
