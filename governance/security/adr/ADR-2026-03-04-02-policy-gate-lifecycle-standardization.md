# ADR-2026-03-04-02: Policy/Gate Lifecycle Standardization

## Status
Accepted

## Context
Policy and gate changes needed a consistent lifecycle definition (propose, approve, deploy, rollback, deprecate) for auditability and predictable operations.

## Decision
- Add `governance/security/POLICY_GATE_LIFECYCLE.md`.
- Treat lifecycle updates as governance artifacts that require review and repository traceability.

## Consequences
- Change-management expectations are explicit and versioned in-repo.
- Operators and reviewers have a stable reference for deployment and rollback behavior.
