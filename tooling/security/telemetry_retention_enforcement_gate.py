#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import time
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

POLICY = ROOT / "governance" / "security" / "telemetry_retention_policy.json"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    sig = POLICY.with_suffix(".json.sig")
    sig_text = sig.read_text(encoding="utf-8").strip()
    if not artifact_signing.verify_file(POLICY, sig_text, key=artifact_signing.current_key(strict=False)):
        if not artifact_signing.verify_file(POLICY, sig_text, key=artifact_signing.bootstrap_key()):
            findings.append("invalid_telemetry_retention_policy_signature")

    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    telemetry = policy.get("ephemeral_sensitive_telemetry", {}) if isinstance(policy, dict) else {}
    if not isinstance(telemetry, dict):
        telemetry = {}
    globs = telemetry.get("scan_globs", []) if isinstance(telemetry.get("scan_globs"), list) else []
    max_age_hours = int(telemetry.get("max_age_hours", 168))

    now = time.time()
    checked = 0
    for glob in globs:
        if not isinstance(glob, str) or not glob.strip():
            continue
        for path in sorted(ROOT.glob(glob)):
            if not path.is_file():
                continue
            checked += 1
            age_hours = int((now - path.stat().st_mtime) // 3600)
            if age_hours > max_age_hours:
                rel = str(path.relative_to(ROOT)).replace("\\", "/")
                findings.append(f"stale_sensitive_telemetry:{rel}:age_hours:{age_hours}:max_hours:{max_age_hours}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_files": checked,
            "max_age_hours": max_age_hours,
        },
        "metadata": {"gate": "telemetry_retention_enforcement_gate"},
    }
    out = evidence_root() / "security" / "telemetry_retention_enforcement_gate.json"
    write_json_report(out, report)
    print(f"TELEMETRY_RETENTION_ENFORCEMENT_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
