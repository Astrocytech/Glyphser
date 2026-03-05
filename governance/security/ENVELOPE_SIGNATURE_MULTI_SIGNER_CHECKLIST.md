# Envelope Signature Multi-Signer Design Checklist

- [x] Define canonical envelope structure (`payload_digest`, `signatures[]`, signer metadata, created timestamp).
- [x] Define signer identity requirements (`key_id`, trust domain, ownership evidence).
- [x] Require deterministic signer ordering and canonical JSON serialization before signature verification.
- [x] Define threshold policy (`M-of-N`) and map thresholds per workflow class.
- [x] Define signer role separation constraints (authorizer vs executor vs auditor).
- [x] Define key rotation behavior for signer set changes across epochs.
- [x] Define revocation behavior when one signer is revoked during validity window.
- [x] Define partial signature failure semantics (reject envelope when threshold unmet).
- [x] Define replay protection requirements for envelope IDs/nonces.
- [x] Define verification evidence output format with per-signer reason codes.
