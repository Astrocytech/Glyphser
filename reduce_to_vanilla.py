#!/usr/bin/env python3
"""Reduce this repository to a minimal, runnable "vanilla" runtime footprint.

Purpose
-------
This utility deletes non-essential files/directories from a full Glyphser checkout,
leaving only the minimum set needed to install and run the core runtime package.

Vanilla definition used by this script
--------------------------------------
The reduced project keeps:
- runtime source code (`runtime/`)
- package metadata (`pyproject.toml`)
- baseline legal and user context (`LICENSE`, `README.md`)
- lockfile (`requirements.lock`)
- this reducer script and its companion README
- `.git/` (if present), to avoid breaking local repository history

Everything else is deleted, then empty directories are removed.

Optional behavior:
- `--keep-tests`: keeps a testable reduced footprint (tests plus required
  dependency regions such as tooling/specs/artifacts/evidence).

Important
---------
- This operation is destructive.
- Run from project root.
- Commit or back up your work first.
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCRIPT_NAME = "reduce_to_vanilla.py"
GUIDE_NAME = "REDUCE_TO_VANILLA.md"

# Exact files kept at repository root.
BASE_KEEP_FILES = {
    "pyproject.toml",
    "LICENSE",
    "README.md",
    "requirements.lock",
    SCRIPT_NAME,
    GUIDE_NAME,
}

# Whole directories kept recursively.
BASE_KEEP_DIRS = {
    "runtime",
    ".git",  # keep local VCS history if present
}

# Additional specific files required for a "testable" reduced profile.
TEST_KEEP_FILES = {
    # Observability + GA baseline evidence dependencies
    "evidence/conformance/reports/latest.json",
    "evidence/deploy/latest.json",
    "evidence/security/latest.json",
    "evidence/recovery/latest.json",
    "evidence/observability/latest.json",
    # External validation baseline dependencies
    "evidence/validation/latest.json",
    "evidence/validation/issues.json",
    "evidence/validation/external_security_review.md",
    "evidence/validation/runs/run-01-linux-mint.json",
    "evidence/validation/runs/run-02-ubuntu-wsl.json",
    "evidence/validation/runs/run-03-docs-only-cleanroom.json",
    "evidence/validation/scorecards/run-01-linux-mint.json",
    "evidence/validation/scorecards/run-02-ubuntu-wsl.json",
    "evidence/validation/scorecards/run-03-docs-only-cleanroom.json",
    # GA policy/report docs consumed by ga_release_gate
    "product/handbook/policies/GA_SUPPORT_MATRIX.md",
    "product/handbook/guides/GA_MIGRATION_GUIDE.md",
    "product/handbook/policies/GA_SUPPORT_LIFECYCLE.md",
    "product/handbook/policies/GA_STATUS_INCIDENT_COMMUNICATION.md",
    "product/handbook/policies/GA_RELEASE_TRAIN_POLICY.md",
    "product/handbook/policies/GA_CONTRACTUAL_SUPPORT_SLA.md",
    "product/handbook/policies/GA_GO_NO_GO_CHECKLIST.md",
    "product/handbook/policies/COMPLIANCE_EVIDENCE_INDEX.md",
    "product/handbook/policies/DEPENDENCY_LICENSE_REVIEW.md",
    "product/handbook/policies/GA_COMPATIBILITY_GUARANTEES.md",
    "product/handbook/policies/POST_GA_GOVERNANCE.md",
    "product/handbook/reports/ACCESSIBILITY_REVIEW.md",
    "product/handbook/policies/SUPPLY_CHAIN_TRUST_POLICY.md",
    "product/handbook/policies/PRIVACY_IMPACT_ASSESSMENT_WORKFLOW.md",
    "product/handbook/policies/DOCS_VERSIONING_POLICY.md",
    "product/handbook/policies/CHANGE_COMMUNICATION_SLA.md",
    "product/handbook/policies/ANNUAL_SECURITY_REVIEW_POLICY.md",
    "product/handbook/policies/GA_SIGNOFF.md",
    "product/handbook/policies/GA_SUPPORT_OPERATIONS_READINESS.md",
    # Observability gate documentation dependencies
    "product/ops/SLOs.md",
    "product/ops/INCIDENT_RESPONSE.md",
}

# Names ignored in traversal safety checks.
PRUNE_NAMES = {".", ".."}


@dataclass
class ChangeSet:
    files_to_delete: list[Path]
    dirs_to_delete: list[Path]


def _rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_kept(path: Path, root: Path, keep_files: set[str], keep_dirs: set[str]) -> bool:
    rel = _rel(path, root)
    if rel in PRUNE_NAMES:
        return True

    if rel in keep_files:
        return True

    for keep_dir in keep_dirs:
        if rel == keep_dir or rel.startswith(f"{keep_dir}/"):
            return True

    return False


def _scan(root: Path, keep_files: set[str], keep_dirs: set[str]) -> ChangeSet:
    files_to_delete: list[Path] = []
    dirs_to_delete: list[Path] = []

    # Collect files/symlinks first.
    for path in sorted(root.rglob("*"), key=lambda p: p.as_posix()):
        if _is_kept(path, root, keep_files, keep_dirs):
            continue
        if path.is_file() or path.is_symlink():
            files_to_delete.append(path)

    # Collect directories bottom-up so children are removed first.
    all_dirs = [
        p for p in root.rglob("*") if p.is_dir() and not _is_kept(p, root, keep_files, keep_dirs)
    ]
    all_dirs.sort(key=lambda p: len(p.parts), reverse=True)
    dirs_to_delete.extend(all_dirs)

    return ChangeSet(files_to_delete=files_to_delete, dirs_to_delete=dirs_to_delete)


def _print_plan(root: Path, changes: ChangeSet, limit: int = 120) -> None:
    total_files = len(changes.files_to_delete)
    total_dirs = len(changes.dirs_to_delete)
    print(f"Plan: delete {total_files} files and remove {total_dirs} directories.")

    if total_files == 0 and total_dirs == 0:
        print("Project is already in vanilla state.")
        return

    print("Sample deletions:")
    shown = 0

    for p in changes.files_to_delete:
        if shown >= limit:
            break
        print(f"  FILE { _rel(p, root) }")
        shown += 1

    for p in changes.dirs_to_delete:
        if shown >= limit:
            break
        print(f"  DIR  { _rel(p, root) }")
        shown += 1

    remaining = total_files + total_dirs - shown
    if remaining > 0:
        print(f"  ... and {remaining} more entries")


def _delete_files(paths: Iterable[Path]) -> int:
    deleted = 0
    for p in paths:
        if not p.exists() and not p.is_symlink():
            continue
        p.unlink(missing_ok=True)
        deleted += 1
    return deleted


def _delete_dirs(paths: Iterable[Path]) -> int:
    deleted = 0
    for d in paths:
        if not d.exists() or not d.is_dir():
            continue

        # Remove only if empty after file cleanup.
        # Never recursively delete here: parent directories may still contain
        # explicitly kept files (for example, evidence baseline files in
        # --keep-tests mode).
        try:
            d.rmdir()
            deleted += 1
        except OSError:
            # Directory is non-empty or in use; leave it in place.
            pass
    return deleted


def _confirm_interactive() -> bool:
    print("This will permanently delete non-vanilla project content.")
    answer = input("Proceed? Type 'yes' to continue: ").strip().lower()
    return answer == "yes"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reduce this repository to minimal vanilla runtime state."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be deleted without deleting anything.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip interactive confirmation.",
    )
    parser.add_argument(
        "--keep-tests",
        action="store_true",
        help="Keep tests/ directory in the reduced project (optional).",
    )
    return parser


def _build_keep_sets(*, keep_tests: bool) -> tuple[set[str], set[str]]:
    keep_files = set(BASE_KEEP_FILES)
    keep_dirs = set(BASE_KEEP_DIRS)
    if keep_tests:
        keep_files.update(TEST_KEEP_FILES)
        # "keep-tests" means testable, not test-files-only.
        # These regions are required by the current test suite imports/fixtures.
        keep_dirs.update(
            {
                "tests",
                "tooling",
                "artifacts",
                "specs",
                "docs",
                "governance",
                "distribution",
            }
        )
    return keep_files, keep_dirs


def main() -> int:
    args = _build_parser().parse_args()
    root = Path(__file__).resolve().parent

    # Guard: ensure script is run from repository root where pyproject exists.
    if not (root / "pyproject.toml").exists() or not (root / "runtime").exists():
        print("ERROR: run this script from Glyphser project root.")
        return 2

    keep_files, keep_dirs = _build_keep_sets(keep_tests=args.keep_tests)
    changes = _scan(root, keep_files, keep_dirs)
    _print_plan(root, changes)

    if args.dry_run:
        print("Dry run complete. No files were changed.")
        return 0

    if len(changes.files_to_delete) == 0 and len(changes.dirs_to_delete) == 0:
        return 0

    if not args.force:
        if not sys.stdin.isatty():
            print("ERROR: non-interactive terminal detected. Use --force to proceed.")
            return 2
        if not _confirm_interactive():
            print("Aborted. No changes made.")
            return 1

    deleted_files = _delete_files(changes.files_to_delete)
    deleted_dirs = _delete_dirs(changes.dirs_to_delete)

    # Final empty-dir cleanup pass (excluding root and kept dirs).
    extra_dirs = [
        p for p in root.rglob("*") if p.is_dir() and not _is_kept(p, root, keep_files, keep_dirs)
    ]
    extra_dirs.sort(key=lambda p: len(p.parts), reverse=True)
    for d in extra_dirs:
        try:
            d.rmdir()
        except OSError:
            pass

    print(f"Done. Deleted {deleted_files} files and removed {deleted_dirs} directories.")
    print("Repository is now in vanilla runtime state.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
