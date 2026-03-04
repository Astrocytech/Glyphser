# Known CI Failure Modes

## SARIF Upload Permissions
- Symptom: `Resource not accessible by integration` during SARIF upload.
- Cause: Missing `security-events: write` or forked PR restrictions.
- Triage:
  - Verify workflow/job permissions include `security-events: write`.
  - Confirm upload is guarded for fork PRs.
  - Ensure SARIF is still uploaded as artifact when code scanning upload is skipped.

## Semgrep Runtime Dependency
- Symptom: `ModuleNotFoundError: No module named 'pkg_resources'`.
- Cause: Missing `setuptools` in security toolchain environment.
- Triage:
  - Run `python tooling/security/install_security_toolchain.py`.
  - Validate with `semgrep --version` and `python -c "import pkg_resources"`.

## Strict Signing Key Missing
- Symptom: strict signing gates fail with missing `GLYPHSER_PROVENANCE_HMAC_KEY`.
- Cause: Secret not configured in lane/environment.
- Triage:
  - Set `GLYPHSER_PROVENANCE_HMAC_KEY` in workflow secret context.
  - For local reproduction, export the variable before running strict gates.

## Evidence Scope Guard Failure
- Symptom: workflow evidence scope gate fails due to non-run-scoped root.
- Cause: `GLYPHSER_EVIDENCE_ROOT` not under `evidence/runs/${{ github.run_id }}/...`.
- Triage:
  - Use run-scoped evidence root and run `evidence_run_dir_guard.py --run-id`.
