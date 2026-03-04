# Security Architecture

This document maps controls to enforcing gates and evidence outputs.

## Control Mapping
- Policy integrity: `tooling/security/policy_signature_gate.py` -> `evidence/security/policy_signature.json`
- Evidence integrity: `tooling/security/evidence_attestation_gate.py`, `tooling/security/evidence_chain_of_custody.py --verify` -> `evidence/security/evidence_attestation_gate.json`, `evidence/security/evidence_chain_of_custody_gate.json`
- Runtime abuse controls: `runtime/glyphser/api/runtime_api.py`, `tooling/security/abuse_telemetry_gate.py` -> `evidence/security/abuse_telemetry.json`
- Provenance integrity: `tooling/security/provenance_signature_gate.py`, `tooling/security/slsa_attestation_gate.py`, `tooling/security/cosign_attestation_gate.py` -> provenance/security evidence artifacts
- Governance markdown control metadata: `tooling/security/governance_markdown_gate.py` -> `evidence/security/governance_markdown_gate.json`
- Review/change control: `tooling/security/review_policy_gate.py` -> `evidence/security/review_policy_gate.json`
- Waiver controls: `tooling/security/temporary_waiver_gate.py` -> `evidence/security/temporary_waiver_gate.json`

## Orchestration
- Primary orchestration gate: `tooling/security/security_super_gate.py`
- CI matrix security lane executes super-gate and uploads all generated security evidence.
