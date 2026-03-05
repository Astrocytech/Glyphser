#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import current_key, key_metadata, sign_file
from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return payload if isinstance(payload, dict) else {}


def _now_utc() -> datetime:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    if fixed:
        try:
            parsed = datetime.fromisoformat(fixed.replace("Z", "+00:00"))
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
        except ValueError:
            pass
    return datetime.now(UTC)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate monthly signed security program health report.")
    parser.add_argument("--strict-key", action="store_true", help="Require strict signing key.")
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    now = _now_utc()
    month = f"{now.year:04d}-{now.month:02d}"
    findings: list[str] = []

    dashboard = _load(sec / "security_dashboard.json")
    if not dashboard:
        findings.append("missing_security_dashboard")
    kpis = dashboard.get("summary", {}).get("kpis", {}) if isinstance(dashboard.get("summary"), dict) else {}
    if not isinstance(kpis, dict):
        kpis = {}
        findings.append("invalid_dashboard_kpis")

    component_reports = {
        "security_dashboard": sec / "security_dashboard.json",
        "security_slo_report": sec / "security_slo_report.json",
        "security_trend_gate": sec / "security_trend_gate.json",
        "security_verification_summary": sec / "security_verification_summary.json",
    }
    component_status: dict[str, str] = {}
    non_pass_components = 0
    for name, path in component_reports.items():
        payload = _load(path)
        status = str(payload.get("status", "MISSING")).upper()
        component_status[name] = status
        if status not in {"PASS", "MISSING"}:
            non_pass_components += 1

    report = {
        "status": "PASS" if not findings and non_pass_components == 0 else "WARN",
        "findings": findings,
        "summary": {
            "month": month,
            "generated_at_utc": now.isoformat(),
            "component_status": component_status,
            "non_pass_components": non_pass_components,
            "kpis": kpis,
        },
        "metadata": {
            "gate": "monthly_security_program_health_report",
            "key_provenance": key_metadata(strict=args.strict_key),
        },
    }
    out = sec / "monthly_security_program_health_report.json"
    write_json_report(out, report)
    sig = sec / "monthly_security_program_health_report.json.sig"
    sig.write_text(sign_file(out, key=current_key(strict=args.strict_key)) + "\n", encoding="utf-8")
    print(f"MONTHLY_SECURITY_PROGRAM_HEALTH_REPORT: {report['status']}")
    print(f"Report: {out}")
    print(f"Signature: {sig}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
