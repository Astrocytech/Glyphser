#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _status(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return "INVALID"
    return str(payload.get("status", "UNKNOWN")).upper() if isinstance(payload, dict) else "INVALID"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    deploy = evidence_root() / "deploy" / "latest.json"
    rollback = evidence_root() / "deploy" / "rollback.json"
    checklist = ROOT / "governance" / "security" / "EMERGENCY_LOCKDOWN_ROLLBACK_CHECKLIST.md"
    statuses = {
        "deploy": _status(deploy),
        "rollback": _status(rollback),
        "provenance_signature": _status(sec / "provenance_signature.json"),
        "policy_signature": _status(sec / "policy_signature.json"),
        "emergency_lockdown": _status(sec / "emergency_lockdown_gate.json"),
    }
    findings = [f"{k}_not_pass" for k, v in statuses.items() if v != "PASS"]
    if not checklist.exists():
        findings.append("missing_emergency_lockdown_rollback_checklist")
    else:
        text = checklist.read_text(encoding="utf-8", errors="ignore")
        if "rollback attestation verification gate" not in text.lower():
            findings.append("rollback_checklist_missing_attestation_step")
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            **statuses,
            "checklist_path": str(checklist.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "release_rollback_provenance_gate"},
    }
    out = sec / "release_rollback_provenance_gate.json"
    write_json_report(out, report)
    print(f"RELEASE_ROLLBACK_PROVENANCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
