# Deterministic Local Reproduction of CI Security Lane

This runbook reproduces the CI security lane locally with deterministic settings.

## 1. Baseline environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.lock
```

Pin deterministic environment variables before running any gate:

```bash
export TZ=UTC
export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export GLYPHSER_STRICT_PREREQS=1
export GLYPHSER_STRICT_KEY=1
```

## 2. Secure developer-mode profile (optional)

If running in developer profile, keep strict checks on and provide explicit mock attestations:

```bash
export GLYPHSER_SECURITY_PROFILE=developer
export GLYPHSER_MOCK_ATTESTATIONS='["mock_policy_signature","mock_provenance_signature","mock_evidence_attestation_index"]'
python tooling/security/developer_mode_profile_gate.py
```

## 3. Reproduce the CI security lane

Run baseline and extended super-gate checks in CI order:

```bash
python tooling/security/security_super_gate.py --strict-prereqs --strict-key
python tooling/security/security_super_gate.py --strict-prereqs --strict-key --include-extended
```

## 4. Required artifacts to inspect

Primary reports:

- `evidence/security/security_super_gate.json`
- `evidence/security/security_verification_summary.json`
- `evidence/security/governance_compliance_delta_report.json`
- `evidence/security/governance_compliance_quarterly_snapshot.json`

## 5. Determinism checks

Re-run the same commands twice and compare digest-stable outputs:

```bash
python tooling/security/security_super_gate.py --only-gate tooling/security/security_toolchain_gate.py
python tooling/security/security_super_gate.py --only-gate tooling/security/security_toolchain_gate.py
```

If output diverges with unchanged repo state and env, treat as a reproducibility regression.
