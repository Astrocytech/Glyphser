# Emergency Bypass Process

## Requirements
- Two approvers: security owner and release owner.
- Explicit reason and blast radius.
- Expiry timestamp in UTC.
- Compensating controls listed.

## Procedure
1. Open incident ticket (`SEC-*` or ADR record).
2. Update `governance/security/emergency_lockdown_policy.json` with reason, approvals, and expiry.
3. Sign policy (`python tooling/security/policy_signature_generate.py --strict-key`).
4. Run `tooling/security/policy_signature_gate.py --strict-key`.
5. Merge with required approvals and monitor `security_super_gate` output.
6. Remove bypass before expiry and re-sign policy.
