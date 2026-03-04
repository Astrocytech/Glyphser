# Evidence Flow Architecture

## Flow
1. Gate execution in CI/maintenance/release writes canonical report JSON into run-scoped evidence root.
2. Signature/index gates sign and attest required artifacts.
3. Super-gate aggregates component outcomes and emits orchestration report.
4. Artifact upload stage publishes signed evidence bundle.
5. Downstream verification gates re-check signatures, integrity chains, and schema conformity.

## Data Path
- Gate output: `evidence/runs/<run_id>/<lane>/security/*.json`
- Signatures: `*.sig` adjacent to signed JSON artifacts.
- Aggregation: `security_super_gate.json`, `security_verification_summary.json(.sig)`
- Chain/index: `evidence_chain_of_custody.json(.sig)`, `evidence_attestation_index.json(.sig)`

## Trust Anchors
- Governance policies under `governance/security/*.json` and `.sig`.
- Signing key material controlled by runtime signing policy and strict-key environment.
- Revocation/rotation controls enforced by dedicated gates.
