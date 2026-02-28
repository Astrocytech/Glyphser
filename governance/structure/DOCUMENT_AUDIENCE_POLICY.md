# Document Audience Policy

This policy defines canonical audience boundaries to prevent cross-domain drift.

## Audience Boundaries
- `specs/`: implementers and integrators; normative technical behavior.
- `governance/`: contributors and maintainers; policy/process/control plane.
- `product/`: customers/operators; external guidance and commitments.
- `evidence/`: auditors/verification consumers; generated proof only.

## Rules
- Product-facing technical docs must reference canonical `specs/` and/or `specs/schemas/` sources.
- Governance docs must not redefine normative runtime behavior already defined in `specs/`.
- Specs must not include contributor process/policy docs; those belong in governance.
- Evidence must never be treated as source-of-truth specification.

## Enforcement
- `tooling/quality_gates/spec_link_gate.py`
- `tooling/quality_gates/spec_schema_map_gate.py`
- `tooling/quality_gates/domain_dependency_gate.py`
