# Document and Code Separation Policy

Goal: keep narrative/process documentation physically separate from executable code.

Rules:
- Documentation files (`.md`, `.txt`, `.rst`) live under `docs/`, `specs/`, `governance/`, or `product/`.
- Executable code (`.py`, shell scripts, and source files) does not live under documentation domains.
- Code directories (`src/`, `tooling/`, `tests/`, `artifacts/generated/`) must not contain documentation files.
- Root-level docs are restricted to governance/community files only.

Enforcement:
- Gate command: `python3 tooling/gates/doc_code_separation_gate.py`
- Report output: `evidence/structure/latest.json`
- Pipeline integration: `tooling/push_button.py`
