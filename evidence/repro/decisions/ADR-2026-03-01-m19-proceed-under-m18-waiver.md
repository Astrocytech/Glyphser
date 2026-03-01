# ADR-2026-03-01: Milestone 19 Execution Under Milestone 18 Waiver

Date: 2026-03-01
Status: Accepted (Temporary)
Owner: Astrocytech/Glyphser

## Context
Milestone 18 is currently BLOCKED/PAUSED due unavailable device classes.
The roadmap objective still requires progress on universality dimensions that are not strictly blocked by those device classes.

## Decision
Allow milestone 19 (Operating System Universality Matrix) to proceed under the active milestone 18 waiver.

## Constraints
- Milestone 18 remains mandatory and must be completed for full universality claims.
- Milestone 19 evidence must explicitly list this waiver in `waivers.json`.
- Final global certification (milestone 25) still requires milestone 18 closure.

## Resume/Closure Conditions
- Milestone 18 resumes when required device-class host manifests become available.
- This ADR closes automatically once milestone 18 is marked DONE and dependency chain returns to normal.

## Consequences
- OS universality work can progress in parallel with hardware acquisition.
- Device universality remains a tracked blocker for full certification.
