# Glyphser

[![CI](https://github.com/Astrocytech/Glyphser/actions/workflows/ci.yml/badge.svg)](https://github.com/Astrocytech/Glyphser/actions/workflows/ci.yml)
[![Conformance Gate](https://github.com/Astrocytech/Glyphser/actions/workflows/conformance-gate.yml/badge.svg)](https://github.com/Astrocytech/Glyphser/actions/workflows/conformance-gate.yml)
[![Schema Gate](https://github.com/Astrocytech/Glyphser/actions/workflows/schema-gate.yml/badge.svg)](https://github.com/Astrocytech/Glyphser/actions/workflows/schema-gate.yml)
[![Release](https://github.com/Astrocytech/Glyphser/actions/workflows/release.yml/badge.svg)](https://github.com/Astrocytech/Glyphser/actions/workflows/release.yml)

Glyphser is a deterministic evidence engine for ML workloads. It guarantees reproducible execution fingerprints across environments by producing cryptographically verifiable runtime manifests.

## Quickstart

```bash
python -m pip install glyphser
```

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

## One-Command Determinism Demo

```bash
glyphser verify hello-core --format text --tree
```

Expected success shape:

```text
VERIFY hello-core: PASS
Evidence: .../artifacts/inputs/fixtures/hello-core
Trace hash: <sha256>
Certificate hash: <sha256>
Interface hash: <sha256>
Evidence files:
  - .../trace.json
  - .../checkpoint.json
  - .../execution_certificate.json
```

## Stable API Boundary

Only modules under `glyphser.public` are considered stable API.

- Stable: `glyphser.public.*` and top-level re-exports from `glyphser`
- Unstable/internal: `glyphser.internal.*`, `runtime.glyphser.*`

See `docs/STABILITY_CONTRACT.md`.

## CLI

- `glyphser verify --model model.json --input input.json`
- `glyphser verify hello-core`
- `glyphser snapshot --model model.json --input input.json --out evidence/snapshot.json`
- `glyphser runtime ...` for advanced operational commands

## Documentation Map

- Concepts: `docs/DOCS_INDEX.md`, `docs/GLOSSARY.md`, `docs/ARCHITECTURE.md`
- API: `docs/API_REFERENCE.md`, `docs/API_STABILITY.md`
- Evidence: `docs/EVIDENCE_FORMATS.md`, `docs/INDEPENDENT_VERIFICATION.md`
- Integrations: `docs/INTEGRATIONS.md`
- Release: `docs/RELEASE_PROCESS.md`, `docs/RELEASE_CHECKLIST.md`, `VERSIONING.md`, `CHANGELOG.md`

## Real Integration Example

- PyTorch deterministic training + evidence flow: `examples/pytorch_determinism.py`

## Development

```bash
python -m pip install -e .[dev]
make release-check
```

## License

GNU AGPL v3.0 (`LICENSE`).
