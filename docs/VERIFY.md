# Verify Glyphser Locally

## Requirements
- Python 3.12+

## Steps
1. Verify deterministic artifacts:
   - `python tools/verify_doc_artifacts.py`
2. Run conformance suite:
   - `python tools/conformance/cli.py run`
   - `python tools/conformance/cli.py verify`
   - `python tools/conformance/cli.py report`
3. Run hello-core end-to-end:
   - `python scripts/run_hello_core.py`

## Expected Result
- All commands exit with status 0.
- The output of `scripts/run_hello_core.py` matches `docs/examples/hello-core/hello-core-golden.json`.
