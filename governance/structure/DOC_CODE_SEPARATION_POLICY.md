# Document and Code Separation Policy

Goal: keep narrative/process documentation physically separate from executable code.

Rules:
- Documentation files (`.md`, `.txt`, `.rst`) live under `docs/` or `document_guidelines/`.
- Executable code (`.py`, shell scripts, and source files) does not live under `docs/` or `document_guidelines/`.
- Code directories (`src/`, `tools/`, `scripts/`, `tests/`, `conformance/`, `artifacts/generated/`) must not contain documentation files.
- Root-level docs are restricted to governance/community files only.

Enforcement:
- Gate command: `python3 tools/doc_code_separation_gate.py`
- Report output: `evidence/structure/latest.json`
- Pipeline integration: `tools/push_button.py`
