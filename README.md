# 𝒢 ⟦·⟧

## Glyphser

Company: **Astrocytech**

Official Astrocytech website: https://www.astrocytech.com

GitHub: https://github.com/Astrocytech/Glyphser

```bash
python -m pip install glyphser
```

```python
from glyphser import verify

model = {
    "ir_hash": "demo-ir",
    "nodes": [
        {"node_id": "x", "instr": "Input", "shape_out": [1], "dtype": "f32"},
    ],
    "outputs": [{"node_id": "x", "output_idx": 0}],
}

result = verify(model, {"x": [1.0]})
print(result.digest)
```

## Stable API Boundary

Only modules under `glyphser.public` are considered stable API.

- Stable: `glyphser.public.*` and top-level re-exports from `glyphser`
- Unstable/internal: `glyphser.internal.*`, `runtime.glyphser.*`

See `docs/API_STABILITY.md` for compatibility guarantees.

## Architecture

```text
User Code
   ↓
Glyphser Public API
   ↓
Runtime Core
   ↓
Deterministic Execution Layer
   ↓
Evidence Builder
   ↓
Conformance Validator
```

Expanded architecture notes: `docs/ARCHITECTURE.md`.

## Real Integration Example

- PyTorch deterministic training + evidence flow: `examples/pytorch_determinism.py`

The example demonstrates:
1. Train a tiny model with fixed seeds.
2. Produce an evidence bundle from model state.
3. Re-run and compare digest values.
4. Fail fast on digest mismatch.

## Installation and CLI

- Package: `pip install glyphser`
- User-facing CLI:
  - `glyphser verify --model model.json --input input.json`
  - `glyphser snapshot --model model.json --input input.json --out evidence/snapshot.json`
- Advanced runtime commands:
  - `glyphser runtime doctor --out evidence/repro/doctor/doctor-manifest.json`
  - `glyphser runtime setup --profile available_local --doctor evidence/repro/doctor/doctor-manifest.json --out evidence/repro/setup/setup-result.json`

## Stability Signals

- Semantic versioning: `VERSIONING.md`
- Changelog: `CHANGELOG.md`
- Compatibility matrix: `docs/COMPATIBILITY_MATRIX.md`
- Deprecation policy: `docs/DEPRECATION_POLICY.md`
- Release and publish process: `docs/RELEASE_PROCESS.md`
- Release checklist: `docs/RELEASE_CHECKLIST.md`
- Auto-generated API reference: `docs/API_REFERENCE.md`
- Security posture: `SECURITY.md`

## Repository Areas

- Core Runtime: `runtime/`
- Public API Package: `glyphser/`
- Compliance & Conformance: `specs/`, `tests/`, `evidence/`
- Research / Experimental: `artifacts/inputs/conformance/suites/`, `specs/layers/L4-*`
- Tooling Automation: `tooling/`
- Governance & Process: `governance/`

## Development

```bash
python -m pip install -e .[dev]
pytest
```

## License

GNU AGPL v3.0 (`LICENSE`).
