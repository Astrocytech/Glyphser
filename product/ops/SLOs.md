# SLOs and Error Budget (Milestone 22)

## SLI Definitions
- Correctness SLI: conformance report status is `PASS` for release pipeline runs.
- Availability SLI: deployment + security baseline gates report `PASS`.
- Recovery SLI: recovery gate report status is `PASS`.

## SLO Targets
- Correctness SLO: 99.9% of release pipeline runs must pass conformance checks.
- Availability SLO: 99.5% of staged deployment checks must pass.
- Recovery SLO: 99.5% of recovery drills must pass.

## Error Budget Policy
- If any SLO falls below target in reporting window, freeze non-critical releases until remediation is verified.
- Error budget review cadence: weekly.

## Alerting Rules
- Emit critical alert on correctness SLO breach.
- Emit high alert on availability/recovery SLO breach.
- Emit heartbeat alert for alerting pipeline health validation.

## Retention and Redaction
- Keep observability reports for minimum 90 days.
- Logs/traces must avoid plaintext secrets and personal data.

