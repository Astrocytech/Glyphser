# Boundary Gates

## Runtime/Tooling Dependency Direction

Rule: runtime modules must not import tooling modules.

Gate command:

```bash
python tooling/quality_gates/runtime_tooling_boundary_gate.py
```

Output:
- `evidence/gates/quality/runtime_tooling_boundary.json`
- `evidence/gates/telemetry/runtime_tooling_boundary.trace.json`
