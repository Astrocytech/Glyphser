# Verify Glyphser Locally

## Requirements
- Python 3.11+
- `git`

## Quick Verify (<=5 steps)
1. Clone and enter repository.
2. Checkout the target release tag or commit.
3. Create and activate a virtual environment.
4. Install project runtime dependencies: `python -m pip install -e .`
5. Run one command: `python tooling/release/verify_release.py`

## Single Command
```bash
python tooling/release/verify_release.py
```

## What It Checks
- Runs `tooling/commands/push_button.py` end-to-end.
- Verifies release artifact hashes against the latest `distribution/release/CHECKSUMS_v*.sha256`.
- Returns exit code `0` only when all checks pass.
