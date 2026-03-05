#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

SECRET_POLICY = ROOT / "governance" / "security" / "secret_management_policy.json"
ROTATION_AUDIT = ROOT / "evidence" / "security" / "secret_rotation_audit.json"
WORKFLOWS = ROOT / ".github" / "workflows"
SECRET_REF = re.compile(r"secrets\.([A-Z0-9_]+)")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_utc(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)


def _age_days(text: str) -> int:
    return int((datetime.now(UTC) - _parse_utc(text)).total_seconds() // 86400)


def _workflow_secret_refs() -> dict[str, list[str]]:
    refs: dict[str, list[str]] = {}
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        names = sorted(set(SECRET_REF.findall(text)))
        if names:
            refs[str(wf.relative_to(ROOT)).replace("\\", "/")] = names
    return refs


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = _load_json(SECRET_POLICY)
    max_age = int(policy.get("max_secret_rotation_age_days", 90))
    audit = _load_json(ROTATION_AUDIT)
    metadata = audit.get("secret_rotation_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    refs = _workflow_secret_refs()
    referenced = sorted({name for names in refs.values() for name in names})

    findings: list[str] = []
    stale: list[str] = []
    for name in referenced:
        entry = metadata.get(name)
        if not isinstance(entry, dict):
            findings.append(f"missing_rotation_metadata_for_referenced_secret:{name}")
            continue
        last = str(entry.get("last_rotated_utc", "")).strip()
        if not last:
            findings.append(f"missing_last_rotated_utc_for_referenced_secret:{name}")
            continue
        try:
            age = _age_days(last)
        except ValueError:
            findings.append(f"invalid_last_rotated_utc_for_referenced_secret:{name}")
            continue
        if age > max_age:
            findings.append(f"stale_referenced_secret:{name}:{age}>{max_age}")
            stale.append(name)

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "workflow_count_with_secret_refs": len(refs),
            "referenced_secret_count": len(referenced),
            "stale_referenced_secret_count": len(stale),
            "max_secret_rotation_age_days": max_age,
        },
        "metadata": {"gate": "stale_secret_usage_wiring_gate"},
        "workflow_secret_references": refs,
    }
    out = evidence_root() / "security" / "stale_secret_usage_wiring_gate.json"
    write_json_report(out, report)
    print(f"STALE_SECRET_USAGE_WIRING_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
