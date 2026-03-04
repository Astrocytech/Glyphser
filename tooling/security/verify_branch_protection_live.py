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
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root


def _api_get(url: str, token: str) -> tuple[int, str]:
    req = urllib.request.Request(
        url,
        method="GET",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return int(resp.status), resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        return int(exc.code), exc.read().decode("utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify live GitHub branch protection against policy.")
    parser.add_argument("--repo", required=True, help="owner/repo")
    parser.add_argument("--branch", default="main")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args([] if argv is None else argv)

    policy = json.loads((ROOT / ".github" / "branch-protection.required.json").read_text(encoding="utf-8"))
    required_checks = policy.get("required_status_checks", [])
    if not isinstance(required_checks, list) or not all(isinstance(x, str) and x for x in required_checks):
        raise ValueError("invalid required_status_checks in policy")

    payload: dict[str, Any] = {"status": "FAIL", "required_status_checks": required_checks, "findings": []}
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

    out = evidence_root() / "security" / "branch_protection_live.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"VERIFY_BRANCH_PROTECTION_LIVE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
