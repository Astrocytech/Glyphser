# Threat Model (Milestone 20)

## Scope
Control surfaces in scope:
- Public API/CLI job control paths.
- State/checkpoint persistence and recovery artifacts.
- Release evidence and signed checksum artifacts.

## Trust Boundaries
- Client to API boundary (token-bearing requests).
- Runtime to persistent storage boundary.
- Runtime to release evidence publishing boundary.

## Threat Scenarios
- Unauthorized action attempts (missing/insufficient role privileges).
- Audit log tampering after event emission.
- Secret leakage in source/config artifacts.
- Corruption of persisted state artifacts.
- Supply-chain artifact substitution (SBOM/provenance mismatch).

## Required Controls
- RBAC authorization checks on all control-surface actions.
- Tamper-evident audit chain verification.
- Secret scanning in baseline security gate.
- Checkpoint/recovery integrity checks (Milestone 19 gate).
- SBOM + build provenance generation in security artifact workflow.

## Severity and Response Targets
- Critical: acknowledge <= 1 business day, patch/mitigate <= 7 days.
- High: acknowledge <= 2 business days, patch/mitigate <= 14 days.
- Medium: acknowledge <= 3 business days, patch/mitigate <= 30 days.
- Low: next scheduled maintenance/release cycle.

