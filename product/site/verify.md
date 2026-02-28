# Verify Glyphser

Status: DRAFT

## Local Verification
- `python tooling/verify_doc_artifacts.py`
- `python tooling/conformance/cli.py run`
- `python tooling/conformance/cli.py verify`
- `python tooling/conformance/cli.py report`
- `python scripts/run_hello_core.py`

## Expected Result
All commands exit with status 0 and match `docs/examples/hello-core/hello-core-golden.json`.
