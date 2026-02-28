# Rollback Runbook (Milestone 21)

## Purpose
Validate deterministic rollback behavior for staging deployment state.

## Procedure
1. Run deploy pipeline:
   - `python tooling/deploy/run_deployment_pipeline.py`
2. Inspect rollback report:
   - `evidence/deploy/rollback.json`
3. Confirm `status` is `PASS`.
4. Confirm drift report:
   - `evidence/deploy/drift.json`
5. Confirm active staging state exists:
   - `artifacts/inputs/reference_states/deploy/staging_active.json`

## Rollback Trigger Threshold
- Use overlay threshold:
- `rollback_error_rate_threshold` from `artifacts/generated/stable/deploy/overlays/staging.json`.

## Post-Rollback Verification
- Re-run deploy pipeline and verify gate still passes.
- Verify bundle hash and overlay policy fields are unchanged unless intentionally updated.
