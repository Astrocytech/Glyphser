# ADR-2026-03-01: Universal Certification Profile `available_local`

## Status
ACCEPTED

## Context
Strict global universality requires hardware/OS targets that are not currently available in the active lab:

- macOS Apple Silicon (`gpu_apple_mps`, iOS tooling),
- additional device classes (`cpu_arm64`, `gpu_amd_rocm`, `gpu_intel`, `edge_target`),
- broader multi-host cluster and strict OS/device expansion set.

The currently available fleet supports meaningful reproducibility validation and certification progress:

- Linux Mint + NVIDIA GTX 1070,
- Ubuntu + NVIDIA RTX 3060 Ti,
- Windows native host (AMD),
- Android target device.

## Decision
Introduce `available_local` as an explicit certification profile for milestones 24 and 25.

- `available_local` is a production certification scope for currently available hardware/OS.
- `strict_universal` remains the long-term full universality scope.
- Deferred strict-only targets remain tracked by existing ADR waivers and milestone backlog.

## Scope and Effects
- Milestone 24:
  - `available_local` PASS requires Android + Web targets.
  - iOS target is strict-track deferred and must be documented in portability gaps.
- Milestone 25:
  - `available_local` prerequisites: `12, 16, 20, 21, 22, 23, 24`.
  - `strict_universal` prerequisites remain full set including `18` and `19`.

## Risk and Mitigation
- Risk: Misinterpretation of `available_local` as full universality.
- Mitigation: All reports include `universality_profile`; strict targets remain explicitly listed as deferred.

## Exit / Revisit Criteria
Revisit this ADR when missing strict targets become available and rerun:

- milestones `18` and `19`,
- milestone `24` in `strict_universal` mode,
- milestone `25` in `strict_universal` mode.
