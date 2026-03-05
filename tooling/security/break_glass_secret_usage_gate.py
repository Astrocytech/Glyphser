#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _enabled(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _verify_signature(path: Path) -> bool:
    sig_path = path.with_suffix(path.suffix + ".sig")
    if not sig_path.exists():
        return False
    signature = sig_path.read_text(encoding="utf-8").strip()
    return verify_file(path, signature, key=current_key(strict=False))


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    usage = _load_json(sec / "break_glass_secret_usage.json")

    env_enabled = _enabled(os.environ.get("GLYPHSER_BREAK_GLASS_SECRET_USED", ""))
    file_enabled = bool(usage.get("break_glass_secret_used", False))
    used = env_enabled or file_enabled

    incident_ticket = str(os.environ.get("GLYPHSER_BREAK_GLASS_INCIDENT_TICKET", "")).strip() or str(
        usage.get("incident_ticket", "")
    ).strip()
    report_rel = str(os.environ.get("GLYPHSER_BREAK_GLASS_AFTER_ACTION_REPORT", "")).strip() or str(
        usage.get("after_action_report", "")
    ).strip()

    findings: list[str] = []
    report_path = ROOT / report_rel if report_rel else None
    report_sig_ok = False

    if used:
        if not incident_ticket:
            findings.append("missing_incident_ticket")
        if not report_rel:
            findings.append("missing_after_action_report_path")
        elif report_path is None or not report_path.exists():
            findings.append("missing_after_action_report")
        else:
            report_sig_ok = _verify_signature(report_path)
            if not report_sig_ok:
                findings.append("invalid_after_action_report_signature")

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "break_glass_secret_used": used,
            "incident_ticket": incident_ticket,
            "after_action_report": report_rel,
            "after_action_report_signature_valid": report_sig_ok,
        },
        "metadata": {"gate": "break_glass_secret_usage_gate"},
    }
    out = sec / "break_glass_secret_usage_gate.json"
    write_json_report(out, payload)
    print(f"BREAK_GLASS_SECRET_USAGE_GATE: {payload['status']}")
    print(f"Report: {out}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
