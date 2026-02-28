# API CLI Command Reference (Milestone 18)

Tool: `python tooling/cli/api_cli.py`

## Global Options
- `--state-path PATH`: optional local state file path.

## Commands

### Submit
```bash
python tooling/cli/api_cli.py submit \
  --payload-file payload.json \
  --token demo-token \
  --scope jobs:write \
  --idempotency-key demo-key-1
```

### Status
```bash
python tooling/cli/api_cli.py status \
  --job-id <JOB_ID> \
  --token demo-token \
  --scope jobs:read
```

### Evidence
```bash
python tooling/cli/api_cli.py evidence \
  --job-id <JOB_ID> \
  --token demo-token \
  --scope evidence:read
```

### Replay
```bash
python tooling/cli/api_cli.py replay \
  --job-id <JOB_ID> \
  --token demo-token \
  --scope replay:run
```
