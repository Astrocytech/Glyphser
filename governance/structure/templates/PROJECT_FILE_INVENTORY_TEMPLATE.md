# Project File Inventory Template

This template defines where inventory evidence is produced and how it is maintained.

## Generation Contract
- Generator command: `python3 tooling/validation/generate_project_inventory.py`
- Output location: `evidence/gates/structure/PROJECT_FILE_INVENTORY.md`
- Pipeline integration: `tooling/commands/push_button.py`

## Structural Requirements
- Inventory output is treated as evidence (generated), not governance policy.
- Governance keeps the generation contract and invariant policy only.
- Inventory must cover the full repository tree excluding transient cache directories.
