#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.client
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root


def _validate_target(repo: str, branch: str, *, dry_run: bool) -> None:
    if "/" not in repo or repo.count("/") != 1:
        raise ValueError("repo must be owner/repo")
    if not branch.strip():
        raise ValueError("branch must be non-empty")
    if not dry_run and repo.strip().lower() == "owner/repo":
        raise ValueError("repo placeholder owner/repo is not allowed in live mode")


def _api_get(url: str, token: str) -> tuple[int, str]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("api URL must be https")
    conn = http.client.HTTPSConnection(parsed.netloc, timeout=30)
    try:
        conn.request(
            "GET",
            parsed.path or "/",
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
            },
        )
        resp = conn.getresponse()
        return int(resp.status), resp.read().decode("utf-8", errors="replace")
    finally:
        conn.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify live GitHub branch protection against policy.")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args([] if argv is None else argv)
    _validate_target(args.repo, args.branch, dry_run=args.dry_run)

    policy = json.loads((ROOT / ".github" / "branch-protection.required.json").read_text(encoding="utf-8"))
    required_checks = policy.get("required_status_checks", [])
    if not isinstance(required_checks, list) or not all(isinstance(x, str) and x for x in required_checks):
        raise ValueError("invalid required_status_checks in policy")

    payload: dict[str, Any] = {
        "status": "FAIL",
        "required_status_checks": required_checks,
        "findings": [],
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    if args.dry_run:
        payload["status"] = "PASS"
        payload["mode"] = "dry_run"
    else:
        token = os.environ.get("GITHUB_TOKEN", "").strip()
        if not token:
            raise ValueError("GITHUB_TOKEN is required unless --dry-run is used")
        url = f"https://api.github.com/repos/{args.repo}/branches/{args.branch}/protection"
        code, body = _api_get(url, token)
        payload["http_status"] = code
        if code >= 400:
            payload["findings"] = [f"github api returned {code}", body]
        else:
            remote = json.loads(body)
            contexts = remote.get("required_status_checks", {}).get("contexts", [])
            if not isinstance(contexts, list):
                contexts = []
            missing = sorted([x for x in required_checks if x not in contexts])
            payload["remote_contexts"] = contexts
            if missing:
                payload["findings"] = [f"missing required contexts: {', '.join(missing)}"]
            else:
                payload["status"] = "PASS"
                payload["mode"] = "live"

    out = evidence_root() / "security" / "branch_protection_live.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"VERIFY_BRANCH_PROTECTION_LIVE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
