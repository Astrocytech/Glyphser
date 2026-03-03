# Glyphser

[![CI](https://github.com/Astrocytech/Glyphser/actions/workflows/ci.yml/badge.svg)](https://github.com/Astrocytech/Glyphser/actions/workflows/ci.yml)
[![Conformance Gate](https://github.com/Astrocytech/Glyphser/actions/workflows/conformance-gate.yml/badge.svg)](https://github.com/Astrocytech/Glyphser/actions/workflows/conformance-gate.yml)
[![Release](https://github.com/Astrocytech/Glyphser/actions/workflows/release.yml/badge.svg)](https://github.com/Astrocytech/Glyphser/actions/workflows/release.yml)
[![PyPI](https://img.shields.io/pypi/v/glyphser)](https://pypi.org/project/glyphser/)
[![Python](https://img.shields.io/pypi/pyversions/glyphser)](https://pypi.org/project/glyphser/)

Glyphser is a deterministic execution verification harness for ML workloads.

It solves one problem: proving whether two runs are meaningfully the same or different, using reproducible evidence hashes instead of manual inspection.

## 60-Second Demo

```bash
glyphser run --example hello --tree
```

Expected shape:

```text
VERIFY hello-core: PASS
Evidence: .../artifacts/inputs/fixtures/hello-core
Trace hash: <sha256>
Certificate hash: <sha256>
Interface hash: <sha256>
```

## Install

```bash
python -m pip install glyphser
```

Quick API usage:

```python
from glyphser import verify

model = {
    "ir_hash": "demo-ir",
    "nodes": [{"node_id": "x", "instr": "Input", "shape_out": [1], "dtype": "f32"}],
    "outputs": [{"node_id": "x", "output_idx": 0}],
}

result = verify(model, {"x": [1.0]})
print(result.digest)
```

## Architecture

```text
User Code
   ↓
Glyphser Public API / CLI
   ↓
Deterministic Runtime Core
   ↓
Evidence Manifests + Hashes
   ↓
Conformance / Verification Gates
```

## Scope (Current)

- Primary scope: single-host, CPU-first deterministic verification.
- Stable API: `glyphser.public.*` and top-level `glyphser` exports.
- User CLI: `glyphser verify`, `glyphser run`, `glyphser snapshot`.

## Advanced Docs

- Docs index: `docs/DOCS_INDEX.md`
- Getting started: `docs/GETTING_STARTED.md`
- Day-1 pathway: `docs/START-HERE.md`
- Proof demo: `docs/PROOF_DEMO.md`
- Pipeline tutorial: `docs/TUTORIAL_PIPELINE.md`
- Quickstart notebook: `notebooks/quickstart.ipynb`
- CI snippets (GitHub/GitLab/Jenkins): `docs/CI_SNIPPETS.md`
- Evidence formats: `docs/EVIDENCE_FORMATS.md`
- Traceability index: `docs/TRACEABILITY.md`
- Evidence metadata catalog: `docs/EVIDENCE_METADATA.md`
- Evidence lifecycle: `docs/EVIDENCE_LIFECYCLE.md`
- Diagrams: `docs/DIAGRAMS.md`
- Docker quickstart: `docs/DOCKER_QUICKSTART.md`
- Alternatives: `docs/ALTERNATIVES.md`
- Use cases: `docs/USE_CASES.md`
- Stability contract: `docs/STABILITY_CONTRACT.md`
- Spec/code matrix: `docs/SPEC_IMPLEMENTATION_MATRIX.md`
- CI integration example: `docs/ci/github-actions-glyphser-gate.yml`
- Public roadmap: `ROADMAP.md`
- Starter issue backlog: `docs/ISSUE_BACKLOG.md`
- Release process: `docs/RELEASE_PROCESS.md`

## License

GNU AGPL v3.0 (`LICENSE`).
