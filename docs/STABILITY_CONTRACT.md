# Stability Contract

## Stable

- Python API under `glyphser.public.*`
- Top-level re-exports from `glyphser`
- CLI commands:
  - `glyphser verify`
  - `glyphser snapshot`
  - `glyphser runtime` (argument surface may evolve, command remains)
- Evidence schemas listed in `docs/EVIDENCE_FORMATS.md`

## Experimental

- `glyphser.internal.*`
- `runtime.glyphser.*`
- `tooling/*` script internals
- Generated or research-layer artifacts under `specs/layers/L4-*`

## Compatibility

- Patch releases are backward-compatible for stable interfaces.
- Minor releases keep stable interfaces compatible unless explicitly deprecated.
- Major releases may remove deprecated interfaces.
