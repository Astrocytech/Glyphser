# Operator Quickstart: Signed Policy and Evidence Artifacts

## Generate/refresh policy signatures
```bash
python tooling/security/policy_signature_generate.py --strict-key
python tooling/security/policy_signature_gate.py --strict-key
```

## Generate/verify evidence attestations
```bash
python tooling/security/security_artifacts.py
python tooling/security/evidence_attestation_index.py --strict-key
python tooling/security/evidence_attestation_gate.py --strict-key
python tooling/security/evidence_chain_of_custody.py --strict-key
python tooling/security/evidence_chain_of_custody.py --verify --strict-key
```

## Run full security orchestration
```bash
python tooling/security/security_super_gate.py --strict-key
```
