# Evidence Storage Policy

## Decision

Chosen policy: **A - versioned audit evidence**.

Rationale:
- Glyphser is an evidence-first system; retaining canonical evidence in git improves audit traceability.
- Deterministic release verification depends on reproducible evidence references.

## Tracked Evidence

The following evidence classes are expected to be tracked:
- metadata catalog (`evidence/metadata/catalog.json`)
- traceability index (`evidence/traceability/index.json`)
- security outputs (`evidence/security/*`)
- quality gate outputs (`evidence/gates/**`)
- benchmark snapshots and archive index (`evidence/benchmarks/**`, `evidence/archive/index.json`)

## Forbidden Paths

Local scratch outputs must not be tracked:
- `evidence/tmp/**`
- `evidence/local/**`
- `evidence/scratch/**`

## Enforcement

Gate command:

```bash
python tooling/quality_gates/evidence_storage_policy_gate.py
```

Outputs:
- `evidence/gates/quality/evidence_storage_policy.json`
- `evidence/gates/telemetry/evidence_storage_policy.trace.json`
