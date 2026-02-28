# External Validation Transcript: Run 02 (Ubuntu WSL)

- Verifier: `external-verifier-b`
- OS: Ubuntu 24.04 (WSL2)
- Runtime profile: `P2_SINGLE_NODE_PROD`
- Mode: guided (not blind)

## Commands
- `python tools/push_button.py`
- `sha256sum conformance/reports/latest.json`
- `cat dist/hello-core-bundle.sha256`
- `cat reports/repro/hashes.txt`

## Outcome
- Pipeline: PASS
- Cross-host reproducibility: PASS (bundle/conformance/repro hashes match reference host)
- Negative-path test: PASS (tampered audit log detected by security baseline gate)
