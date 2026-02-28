# External Validation Transcript: Run 03 (Docs-Only Cleanroom)

- Verifier: `external-verifier-c`
- OS: Debian 12
- Runtime profile: `P1_LOCAL_DEV`
- Mode: blind + docs-only

## Commands (from docs only)
- `python tooling/verify_release.py`
- `python tooling/api_cli.py submit --payload-file payload.json --token role:operator --scope jobs:write`
- `python tooling/api_cli.py status --job-id <job_id> --token role:auditor --scope jobs:read`
- `python tooling/api_cli.py replay --job-id <job_id> --token role:operator --scope replay:run`

## Outcome
- Verify flow: PASS
- API CLI flow: PASS
- Negative-path test: PASS (viewer token denied `jobs:write`)
- No maintainer intervention required.
