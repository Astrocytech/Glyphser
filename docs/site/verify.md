# Verify Glyphser

Status: DRAFT

## Local Verification
- `python tools/verify_doc_artifacts.py`
- `python tools/conformance/cli.py run`
- `python tools/conformance/cli.py verify`
- `python tools/conformance/cli.py report`
- `python scripts/run_hello_core.py`

## Expected Result
All commands exit with status 0 and match `docs/examples/hello-core/hello-core-golden.json`.
