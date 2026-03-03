# Gate Telemetry

Every quality gate now emits a structured telemetry trace file.

## Location

- `evidence/gates/telemetry/<gate_id>.trace.json`

## Contents

- `status`
- `findings`
- `failure_taxonomy`
- `recommended_next_steps`
- full raw report payload

## Purpose

- Speed up RCA for gate failures.
- Standardize failure categories and remediation guidance.
