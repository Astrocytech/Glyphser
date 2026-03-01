# ADR-2026-03-01: Milestone 12 Temporary Waiver (Resource Gap)

Date: 2026-03-01
Status: Accepted (Temporary)
Owner: Astrocytech/Glyphser

## Context
Milestone 12 (Multi-Host and Multi-OS Matrix) requires:
- at least 2 Linux hosts,
- at least 1 Windows host,
- at least 2 GPU architectures including GTX 1070 baseline and RTX 30+.

Current available hardware does not satisfy this matrix.

## Decision
Apply a temporary waiver so milestones 13-15 may proceed while milestone 12 remains BLOCKED.

## Constraints
- Milestone 12 remains mandatory for universal certification.
- Milestone 16 cannot be marked DONE until milestone 12 is completed and this waiver is closed.
- All milestone 13-15 reports must include `waivers.json` referencing this ADR.

## Resume Criteria for Milestone 12
- Collect host manifests meeting matrix requirements.
- Re-run `tooling/scripts/repro/compare_multi_host_multi_os_matrix.py` with all manifests.
- Achieve PASS with required profile coverage and GPU architecture checks.

## Consequences
- Program velocity is preserved for framework/language work.
- Universal profile certification remains gated by cross-host universalization evidence.
