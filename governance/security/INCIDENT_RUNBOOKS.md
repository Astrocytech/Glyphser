# Gate Family Incident Runbooks

## Signature/Policy failures
- Run: `policy_signature_gate`, `governance_markdown_gate`.
- Actions: verify keys, regenerate signatures, inspect tamper evidence.

## Evidence integrity failures
- Run: `evidence_attestation_gate`, `evidence_chain_of_custody --verify`.
- Actions: isolate run artifacts, compare chain tip hash, re-materialize evidence.

## Abuse/replay failures
- Run: `abuse_telemetry_gate`, runtime API audit checks.
- Actions: enable lockdown policy if needed, rotate tokens, increase scrutiny.

## Supply-chain/provenance failures
- Run: `provenance_signature_gate`, `slsa_attestation_gate`, `cosign_attestation_gate`, `provenance_revocation_gate`.
- Actions: block release, revoke compromised artifacts/keys, rebuild provenance.
