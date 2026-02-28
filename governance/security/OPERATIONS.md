# Security Operations (Milestone 20)

## Authentication and Authorization Baseline
- Bearer-token style identity input is required for API/CLI operations.
- RBAC actions are enforced via deterministic role-permission policy.
- Privileged actions require `admin` role.

## Audit Logging
- Security-relevant operations emit hash-chained audit events.
- Audit chain verification must pass in CI/security gate.
- Tamper detection is a release-blocking condition.

## Key and Secret Operations
- Secret scanning runs as part of security baseline gate.
- Key rotation cadence: every 90 days for signing/operational keys.
- Key compromise response:
- Rotate compromised key immediately.
- Revoke trust for compromised key material.
- Re-sign affected release artifacts where applicable.

## Access Review and Exceptions
- Access review cadence: monthly for privileged service/user roles.
- Security exception process requires:
- explicit approval owner,
- expiry date,
- compensating controls,
- closure verification.

## Vulnerability and Remediation Policy
- Vulnerability remediation SLA is severity-based (see `THREAT_MODEL.md`).
- Security gate output is tracked in `evidence/security/latest.json`.
- Independent security review cadence: annual minimum.

