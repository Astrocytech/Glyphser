# Glyphser

Company: **Astrocytech**


Conformance: PASS (local)
Hello-core: PASS (local)
Release bundle: PASS (local)

This repository contains the deterministic runtime specifications, capability contracts, and conformance tooling for the Glyphser ecosystem, maintained by Astrocytech.

GitHub: https://github.com/Astrocytech/Glyphser

Independent implementation; no official affiliation or certification claims are made unless explicitly stated.

## Quick Start
1. Ensure you have Python 3.12+
2. Install dependencies: `pip install -e .`
3. Run sanity checks: `python tooling/validation/validate_data_integrity.py`
4. Run the full push-button pipeline: `python tooling/commands/push_button.py`

## You Are Here
- `runtime/`: runtime Python package (`glyphser`).
- `specs/`: human-readable normative specifications and contracts.
- `specs/schemas/`: machine-readable schemas aligned to spec layers.
- `artifacts/`: deterministic inputs, expected outputs, generated bundles.
- `evidence/`: generated proof/reports from validation pipelines.
- `tooling/`: automation, gates, codegen, deploy and release tooling.
- `governance/`: policy, roadmap, structure rules and ecosystem metadata.
- `product/`: external-facing docs, runbooks, and site content.
- `distribution/`: release and signing material.
- `tests/`: executable validation suites (docs intentionally excluded by policy).

## Layer Map
- `specs/layers/L1-foundation/`: core interfaces and canonical data rules.
- `specs/layers/L2-specs/`: runtime and system specifications.
- `specs/layers/L3-tests/`: test plans, conformance matrices, release gates.
- `specs/layers/L4-implementation/`: implementation guides and operations references.
- `specs/schemas/layers/L1..L4/`: machine schemas corresponding to L1..L4 scope.
