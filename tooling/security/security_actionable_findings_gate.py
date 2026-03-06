#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
REASON_CODE_RE = re.compile(r"^[a-z0-9][a-z0-9_.-]{0,63}$")


def _is_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    checked_fail = 0
    checked_warn = 0

    for path in sorted(sec.glob("*.json")):
        if path.name == "security_actionable_findings_gate.json":
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not isinstance(payload, dict):
            continue
        status = str(payload.get("status", "")).upper()
        if status not in {"FAIL", "WARN"}:
            continue
        report_findings = payload.get("findings", [])
        if not isinstance(report_findings, list) or not report_findings:
            findings.append(f"missing_{status.lower()}_findings:{path.name}")
            continue
        summary = payload.get("summary")
        if not isinstance(summary, dict):
            findings.append(f"missing_summary:{path.name}")
        else:
            finding_count = summary.get("finding_count")
            if not isinstance(finding_count, int) or isinstance(finding_count, bool):
                findings.append(f"missing_summary_finding_count:{path.name}")
            elif finding_count != len(report_findings):
                findings.append(
                    f"summary_finding_count_mismatch:{path.name}:expected={len(report_findings)}:actual={finding_count}"
                )
        metadata = payload.get("metadata")
        if not isinstance(metadata, dict):
            findings.append(f"missing_metadata:{path.name}")
            metadata = {}
        gate_version = str(metadata.get("gate_version", "")).strip()
        if not gate_version:
            findings.append(f"missing_gate_version:{path.name}")
        execution_context = metadata.get("execution_context")
        if not isinstance(execution_context, dict) or not execution_context:
            findings.append(f"missing_execution_context:{path.name}")
        for idx, item in enumerate(report_findings):
            s = str(item).strip()
            if not s or ":" not in s:
                findings.append(f"non_actionable_finding:{path.name}:{idx}")
                continue
            reason_code = s.split(":", 1)[0].strip()
            if not REASON_CODE_RE.fullmatch(reason_code):
                findings.append(f"invalid_reason_code:{path.name}:{idx}")
        if status == "FAIL":
            checked_fail += 1
            continue

        checked_warn += 1
        rationale = str(metadata.get("downgrade_rationale", "")).strip()
        expiry = str(metadata.get("downgrade_expiry", "")).strip()
        if not rationale:
            findings.append(f"missing_warn_downgrade_rationale:{path.name}")
        if not expiry or not _is_iso_date(expiry):
            findings.append(f"missing_or_invalid_warn_downgrade_expiry:{path.name}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_failed_reports": checked_fail,
            "checked_warn_reports": checked_warn,
        },
        "metadata": {"gate": "security_actionable_findings_gate"},
    }
    out = sec / "security_actionable_findings_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_ACTIONABLE_FINDINGS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
