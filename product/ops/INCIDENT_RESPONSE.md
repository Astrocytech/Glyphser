# Incident Response (Milestone 22)

## Purpose
Define deterministic incident handling flow for alert-triggered failures in correctness, availability, or recovery gates.

## Severity Model
- `SEV-1`: correctness SLO breach affecting release trust.
- `SEV-2`: deployment/security/recovery gate breach with mitigation available.
- `SEV-3`: isolated test signal degradation without customer impact.

## Response Flow
1. Detect and acknowledge alert.
2. Classify severity and assign owner.
3. Collect deterministic evidence artifacts from reports.
4. Mitigate:
- rollback deployment state when needed,
- patch and rerun failing gate,
- verify restored PASS status.
5. Publish postmortem summary with corrective actions.

## Mandatory Incident Artifacts
- `reports/observability/latest.json`
- `reports/observability/alert_test.json`
- `reports/observability/incident_drill.json`
- relevant source gate reports (deploy/security/recovery/conformance)

## Drill Requirement
- Run at least one alert triage drill per milestone iteration and store report in `reports/observability/`.

