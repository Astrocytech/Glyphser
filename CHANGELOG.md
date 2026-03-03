# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

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
