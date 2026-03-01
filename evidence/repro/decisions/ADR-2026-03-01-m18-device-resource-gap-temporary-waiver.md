# ADR-2026-03-01: Milestone 18 Temporary Waiver (Device Resource Gap)

Date: 2026-03-01
Status: Accepted (Temporary)
Owner: Astrocytech/Glyphser

## Context
Milestone 18 (Device-Class Expansion Matrix) requires coverage of:
- cpu_arm64,
- gpu_amd_rocm,
- gpu_apple_mps,
- edge_target,
in addition to currently available classes.

Current hardware inventory does not include all required device classes.

## Decision
Apply a temporary waiver so roadmap execution can continue while milestone 18 remains BLOCKED/PAUSED.

## Constraints
- Milestone 18 remains mandatory for full universality claims.
- Any milestone or certification claiming "all devices" must not move to DONE until milestone 18 is completed and this waiver is closed.
- All downstream milestone reports must list this waiver in `waivers.json` when applicable.

## Resume Criteria for Milestone 18
- Collect host manifests for missing required device classes.
- Re-run `tooling/scripts/repro/compare_device_class_expansion.py` with aggregated manifests.
- Achieve PASS with no missing required device classes.

## Consequences
- Program can continue on software/library/language axes.
- Device universality certification remains deferred until hardware coverage is complete.
