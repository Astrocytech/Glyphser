# Verify Glyphser

Status: DRAFT

## Local Verification
- `python tooling/docs/verify_doc_artifacts.py`
- `python tooling/conformance/cli.py run`
- `python tooling/conformance/cli.py verify`
- `python tooling/conformance/cli.py report`
- `python tooling/scripts/run_hello_core.py`

## Expected Result
All commands exit with status 0 and match `docs/examples/hello-core/hello-core-golden.json`.

Canonical source references: `specs/` and `specs/schemas/` define normative behavior for this document.
