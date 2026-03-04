# ADR-2026-03-04-01: Threat-Control Mapping Gate

## Status
Accepted

## Context
Security controls were distributed across policies, gates, workflows, and evidence artifacts without a single machine-checkable mapping.

## Decision
- Introduce `governance/security/threat_control_matrix.json` as the canonical control map.
- Add `tooling/security/threat_control_mapping_gate.py` to validate:
  - control IDs are stable and mapped
  - mapped gates exist and are present in super-gate manifest
  - mapped workflows reference mapped gates
  - critical gates always have at least one owning control
  - threat model metadata control IDs remain in sync with matrix IDs

## Consequences
- Drift between threat model and workflow wiring becomes an explicit CI failure.
- Ownership/accountability for critical controls is continuously enforced.
