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


def _check_http(name: str, url: str, token: str) -> dict[str, Any]:
    req = urllib.request.Request(url, method="GET")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return {"name": name, "ok": int(resp.status) < 400, "status_code": int(resp.status)}
    except urllib.error.HTTPError as exc:
        return {"name": name, "ok": False, "status_code": int(exc.code)}
    except Exception as exc:  # pragma: no cover
        return {"name": name, "ok": False, "error": str(exc)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify live security integrations (WAF/SIEM/Paging).")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args([] if argv is None else argv)

    checks: list[dict[str, Any]] = []
    if args.dry_run:
        checks = [
            {"name": "waf_ingress", "ok": True, "mode": "dry_run"},
            {"name": "siem_pipeline", "ok": True, "mode": "dry_run"},
            {"name": "oncall_paging", "ok": True, "mode": "dry_run"},
        ]
    else:
        checks.append(
            _check_http(
                "waf_ingress",
                os.environ.get("GLYPHSER_WAF_HEALTH_URL", ""),
                os.environ.get("GLYPHSER_WAF_TOKEN", ""),
            )
        )
        checks.append(
            _check_http(
                "siem_pipeline",
                os.environ.get("GLYPHSER_SIEM_HEALTH_URL", ""),
                os.environ.get("GLYPHSER_SIEM_TOKEN", ""),
            )
        )
        checks.append(
            _check_http(
                "oncall_paging",
                os.environ.get("GLYPHSER_PAGING_HEALTH_URL", ""),
                os.environ.get("GLYPHSER_PAGING_TOKEN", ""),
            )
        )

    status = "PASS" if all(bool(c.get("ok")) for c in checks) else "FAIL"
    payload = {"status": status, "checks": checks}
    out = evidence_root() / "security" / "live_integrations.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"LIVE_INTEGRATIONS_VERIFY: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
