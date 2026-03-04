#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.client
import importlib
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

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _validate_live_url(name: str, url: str) -> None:
    cleaned = url.strip()
    if not cleaned:
        raise ValueError(f"missing required URL for {name}")
    if not cleaned.startswith("https://"):
        raise ValueError(f"{name} URL must start with https://")
    lowered = cleaned.lower()
    if "example.com" in lowered or "placeholder" in lowered:
        raise ValueError(f"{name} URL appears to be placeholder data")


def _check_http(name: str, url: str, token: str) -> dict[str, Any]:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        return {"name": name, "ok": False, "error": "invalid_url_scheme"}
    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    conn = http.client.HTTPSConnection(parsed.netloc, timeout=15)
    try:
        conn.request("GET", parsed.path or "/", headers=headers)
        resp = conn.getresponse()
        return {"name": name, "ok": int(resp.status) < 400, "status_code": int(resp.status)}
    except Exception as exc:  # pragma: no cover
        return {"name": name, "ok": False, "error": str(exc)}
    finally:
        conn.close()


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
        required_env = [
            "GLYPHSER_WAF_HEALTH_URL",
            "GLYPHSER_SIEM_HEALTH_URL",
            "GLYPHSER_PAGING_HEALTH_URL",
        ]
        missing = [name for name in required_env if not os.environ.get(name, "").strip()]
        if missing:
            raise ValueError(f"missing required live integration env vars: {', '.join(missing)}")
        _validate_live_url("waf_ingress", os.environ.get("GLYPHSER_WAF_HEALTH_URL", ""))
        _validate_live_url("siem_pipeline", os.environ.get("GLYPHSER_SIEM_HEALTH_URL", ""))
        _validate_live_url("oncall_paging", os.environ.get("GLYPHSER_PAGING_HEALTH_URL", ""))
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
    payload = {
        "status": status,
        "findings": [] if status == "PASS" else [f"integration_check_failed:{c.get('name', 'unknown')}" for c in checks if not c.get("ok")],
        "summary": {"checks": checks, "mode": "dry_run" if args.dry_run else "live", "checked_at_utc": datetime.now(UTC).isoformat()},
        "metadata": {"gate": "live_integrations_verify"},
        "checks": checks,
        "mode": "dry_run" if args.dry_run else "live",
        "checked_at_utc": datetime.now(UTC).isoformat(),
    }
    out = evidence_root() / "security" / "live_integrations.json"
    write_json_report(out, payload)
    print(f"LIVE_INTEGRATIONS_VERIFY: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
