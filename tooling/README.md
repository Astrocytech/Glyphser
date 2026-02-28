# Tooling

Automation entrypoint for gates, code generation, conformance, deployment, and release.

## Subdomains
- `tooling/gates/`: structural/spec/runtime policy enforcement.
- `tooling/codegen/`: schema/contract-driven generator pipeline.
- `tooling/conformance/`: conformance runner and report generation.
- `tooling/deploy/`: deployment manifest/profile/rollback pipeline.
- `tooling/release/`: release bundle and release evidence gates.
- `tooling/security/`: security artifacts and baseline checks.
- `tooling/validation/`: validation utilities (including inventory generation).

## Primary Command
- `python tooling/commands/push_button.py`
