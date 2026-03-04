#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _validate_target(repo: str, branch: str, *, dry_run: bool) -> None:
    if "/" not in repo or repo.count("/") != 1:
        raise ValueError("repo must be owner/repo")
    if not branch.strip():
        raise ValueError("branch must be non-empty")
    if not dry_run and repo.strip().lower() == "owner/repo":
        raise ValueError("repo placeholder owner/repo is not allowed in live mode")


def _load_policy() -> dict[str, Any]:
    path = ROOT / ".github" / "branch-protection.required.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("invalid branch protection policy")
    return payload


def _api_request(url: str, *, method: str, token: str, payload: dict[str, Any]) -> tuple[int, str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return int(resp.status), body
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        return int(exc.code), body


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Apply branch protection rules from repository policy file.")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args([] if argv is None else argv)
    _validate_target(args.repo, args.branch, dry_run=args.dry_run)

    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token and not args.dry_run:
        raise ValueError("GITHUB_TOKEN is required unless --dry-run is used")

    policy = _load_policy()
    checks = policy.get("required_status_checks", [])
    if not isinstance(checks, list) or not all(isinstance(x, str) and x for x in checks):
        raise ValueError("required_status_checks must be list[str]")

    payload = {
        "required_status_checks": {"strict": True, "contexts": checks},
        "enforce_admins": True,
        "required_pull_request_reviews": {
            "dismiss_stale_reviews": True,
            "require_code_owner_reviews": True,
            "required_approving_review_count": 1,
        },
        "restrictions": None,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
    }

    if args.dry_run:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0

    url = f"https://api.github.com/repos/{args.repo}/branches/{args.branch}/protection"
    status, body = _api_request(url, method="PUT", token=token, payload=payload)
    print(f"apply_branch_protection status={status}")
    if status >= 400:
        print(body)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
