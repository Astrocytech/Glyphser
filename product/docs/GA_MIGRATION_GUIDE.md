# GA Migration Guide (v0.x -> v0.1.0)

1. Backup existing state and evidence directories.
2. Pull tag `v0.1.0` and recreate virtual environment with Python 3.12.
3. Run `python3 tools/push_button.py` and confirm all gates pass.
4. Validate release bundle hash with `docs/release/CHECKSUMS_v0.1.0.sha256`.
5. Switch production workflow to GA tag and keep rollback target at prior v0.x commit.

Rollback: restore previous checkout and restore backed-up state snapshot.
