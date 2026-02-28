# Rollback Runbook (Milestone 21)

## Purpose
Validate deterministic rollback behavior for staging deployment state.

## Procedure
1. Run deploy pipeline:
   - `python tools/deploy/run_deployment_pipeline.py`
2. Inspect rollback report:
   - `reports/deploy/rollback.json`
3. Confirm `status` is `PASS`.
4. Confirm drift report:
   - `reports/deploy/drift.json`
5. Confirm active staging state exists:
   - `reports/deploy/state/staging_active.json`

## Rollback Trigger Threshold
- Use overlay threshold:
- `rollback_error_rate_threshold` from `generated/deploy/overlays/staging.json`.

## Post-Rollback Verification
- Re-run deploy pipeline and verify gate still passes.
- Verify bundle hash and overlay policy fields are unchanged unless intentionally updated.
