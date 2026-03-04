# Security Gate Onboarding Checklist

Use this checklist when adding any new file under `tooling/security/*_gate.py`.

1. Add gate implementation with deterministic output writing.
2. Ensure report includes `status`, `findings`, `summary`, and `metadata`.
3. Include `metadata.gate` identifier and schema-compatible fields.
4. Add unit tests under `tests/security/` for pass and fail paths.
5. Update `tooling/security/security_super_gate.py` and `security_super_gate_manifest.json` when the gate is part of core or extended execution.
6. Update workflow wiring tests when CI/release/security-maintenance step wiring changes.
7. Add/refresh policy files and signatures when gate behavior is policy-driven.
8. Record TODO progress in the hardening master TODO index.
