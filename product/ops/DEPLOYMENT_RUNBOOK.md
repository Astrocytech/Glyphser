# Deployment Runbook (Milestone 21)

## One-Command Deploy Validation
```bash
python tools/deploy/run_deployment_pipeline.py
```

Expected output includes:
- profile bundle generation success
- overlay generation (`dev`, `staging`, `prod`)
- staging deploy/rollback gate pass

## Staging Health/Readiness Checks
- Health: artifact presence and hash verification from bundle manifest.
- Readiness: overlay policy fields present (`rollout_strategy`, rollback thresholds, quotas, budget alarm).

## Rollout Policy
- Staging default: canary with capped parallel rollout.
- Production default: blue-green (defined in prod overlay).

## Immutable Artifacts
- Deployment references hash-addressed bundle manifest entries.
- Candidate bundle hash is persisted in deployment reports.

## Required Evidence
- `reports/deploy/latest.json`
- `reports/deploy/rollback.json`
- `reports/deploy/drift.json`
- `reports/deploy/parity.json`
