# Reduce Project to Vanilla State

This document explains `reduce_to_vanilla.py`, a root-level utility that trims the repository down to the minimum runtime footprint.

## What "Vanilla State" Means
After reduction, the project keeps only:
- `runtime/`
- `pyproject.toml`
- `LICENSE`
- `README.md`
- `requirements.lock`
- `reduce_to_vanilla.py`
- `REDUCE_TO_VANILLA.md`
- `.git/` (if present)

Everything else is deleted, and empty directories are removed.

Optional:
- `--keep-tests` preserves a **testable** reduced footprint, keeping:
  - `tests/`
  - `tooling/`
  - `artifacts/`
  - `specs/`
  - `docs/`
  - `governance/`
  - `distribution/`
  - minimal required GA/observability/external-validation baseline files under `evidence/` and `product/`

Note: `evidence/` is not preserved wholesale in `--keep-tests` mode. A minimal baseline is retained (including `evidence/conformance/reports/latest.json`) so gate-driven tests can run, and additional evidence is regenerated at runtime.

## Why Use This
Use this when you want:
- a minimal runtime-only project tree (default), or
- a reduced-but-testable tree (`--keep-tests`).

## Usage
Run from project root:

Preview only:
```bash
python reduce_to_vanilla.py --dry-run
```

Run interactively (asks for confirmation):
```bash
python reduce_to_vanilla.py
```

Run non-interactively (force deletion):
```bash
python reduce_to_vanilla.py --force
```

Keep tests while reducing:
```bash
python reduce_to_vanilla.py --keep-tests
```

Keep tests in non-interactive mode:
```bash
python reduce_to_vanilla.py --keep-tests --force
```

## Safety Notes
- This is destructive.
- Commit or back up before running.
- If you need full validation pipelines later, keep a full copy of the repository.
