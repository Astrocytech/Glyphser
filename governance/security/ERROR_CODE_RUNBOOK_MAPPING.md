# Security Error Code to Runbook Mapping

All security gate reports use machine-readable codes in `metadata.error_codes`.
Each code is normalized as `sec_<finding_tokenized>` and is also tagged with
`metadata.failure_classification` and `metadata.failure_classification_set`.

This table is the required mapping from every emitted error code to runbook section.
The mapping is performed by top-level failure classification.

| Failure Classification | Meaning | Runbook Section |
|---|---|---|
| `prereq_failure` | Missing prerequisites, environment variables, toolchain, or required artifacts. | `governance/security/GATE_RUNBOOK_INDEX.md` |
| `infra_failure` | Transient infrastructure/runtime issues (timeouts, network, transport, unavailable dependencies). | `governance/security/INCIDENT_RUNBOOKS.md` |
| `policy_failure` | Policy/signature/schema/governance validation failures. | `governance/security/POLICY_GATE_LIFECYCLE.md` |
| `control_failure` | Security control logic failures not covered by prereq/infra/policy categories. | `governance/security/OPERATIONS.md` |

## Deterministic Mapping Rule
1. Read `metadata.failure_classification` from the security report.
2. Use the table above to route every code in `metadata.error_codes` to its runbook section.
3. If `metadata.failure_classification_set` contains multiple classes, triage all listed sections.

## Examples
- `sec_missing_tool_semgrep` -> `prereq_failure` -> `governance/security/GATE_RUNBOOK_INDEX.md`
- `sec_network_timeout_upstream_scanner` -> `infra_failure` -> `governance/security/INCIDENT_RUNBOOKS.md`
- `sec_policy_signature_invalid` -> `policy_failure` -> `governance/security/POLICY_GATE_LIFECYCLE.md`
- `sec_stale_attestation_evidence_security_a_sig_999h` -> `control_failure` -> `governance/security/OPERATIONS.md`
