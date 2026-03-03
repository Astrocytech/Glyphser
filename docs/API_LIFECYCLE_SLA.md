# API Lifecycle SLA

Public API lifecycle guarantees are defined by:
- `specs/contracts/interface_stability_sla.json`
- `docs/DEPRECATION_POLICY.md`

## Commitments

- Stable exports under top-level `glyphser` remain compatible within minor lines.
- Breaking changes require a major version bump.
- Deprecated aliases remain available for at least one minor release window.

## Validation

Run:

```bash
python tooling/quality_gates/interface_stability_gate.py
```
