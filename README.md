# Glyphser

Company: **Astrocytech**

![Glyphser logo](assets/glyphser3.svg)

Conformance: PASS (local)
Hello-core: PASS (local)
Release bundle: PASS (local)

This repository contains the deterministic runtime specifications, capability contracts, and conformance tooling for the Glyphser ecosystem, maintained by Astrocytech.

Independent implementation; no official affiliation or certification claims are made unless explicitly stated.

## Quick Start
1. Ensure you have Python 3.12+
2. Install dependencies: `pip install -e .`
3. Run sanity checks: `python tools/validate_data_integrity.py`

## Structure
* `contracts/`: CBOR/JSON source of truth for capabilities.
* `docs/`: Layered specification architecture.
* `tools/`: Automation and verification suite.
