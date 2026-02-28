# External Validation Transcript: Run 01 (Linux Mint)

- Verifier: `external-verifier-a`
- OS: Linux Mint 22.1
- Runtime profile: `P2_SINGLE_NODE_PROD`
- Mode: guided (not blind)

## Commands
- `python tooling/commands/push_button.py`
- `sha256sum evidence/conformance/reports/latest.json`
- `cat artifacts/bundles/hello-core-bundle.sha256`
- `cat evidence/repro/hashes.txt`

## Outcome
- Pipeline: PASS
- Hash checks: PASS
- Negative-path test: PASS (invalid role token rejected for write action)
