#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
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
ORG_POLICY = ROOT / "governance" / "security" / "org_secret_backend_policy.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_utc(text: str) -> datetime:
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(UTC)


def _age_days(text: str) -> int:
    return int((datetime.now(UTC) - _parse_utc(text)).total_seconds() // 86400)


def _required_secret_names() -> list[str]:
    out: set[str] = set()
    for path in (SECRET_POLICY, ORG_POLICY):
        payload = _load_json(path)
        required = payload.get("required_secrets", [])
        if isinstance(required, list):
            for item in required:
                if isinstance(item, str) and item.strip():
                    out.add(item.strip())
    return sorted(out)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec_policy = _load_json(SECRET_POLICY)
    max_age = int(sec_policy.get("max_secret_rotation_age_days", 90))
    audit_rel = str(sec_policy.get("rotation_audit_log", "evidence/security/secret_rotation_audit.json")).strip()
    audit = _load_json(ROOT / audit_rel)

    required = _required_secret_names()
    rotated = audit.get("secrets_rotated", [])
    if not isinstance(rotated, list):
        rotated = []
    rotated_set = {str(item).strip() for item in rotated if isinstance(item, str) and str(item).strip()}

    metadata = audit.get("secret_rotation_metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    findings: list[str] = []
    for name in required:
        if name not in rotated_set:
            findings.append(f"required_secret_not_rotated:{name}")
        details = metadata.get(name)
        if not isinstance(details, dict):
            findings.append(f"missing_rotation_metadata:{name}")
            continue
        last_rotated = str(details.get("last_rotated_utc", "")).strip()
        method = str(details.get("rotation_method", "")).strip()
        ticket = str(details.get("rotation_ticket", "")).strip()
        if not last_rotated:
            findings.append(f"missing_last_rotated_utc:{name}")
        else:
            try:
                age = _age_days(last_rotated)
            except ValueError:
                findings.append(f"invalid_last_rotated_utc:{name}")
            else:
                if age > max_age:
                    findings.append(f"stale_last_rotated_utc:{name}:{age}>{max_age}")
        if not method:
            findings.append(f"missing_rotation_method:{name}")
        if not ticket:
            findings.append(f"missing_rotation_ticket:{name}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_secret_count": len(required),
            "rotated_secret_count": len(rotated_set),
            "metadata_secret_count": len(metadata),
            "max_secret_rotation_age_days": max_age,
        },
        "metadata": {"gate": "secret_rotation_metadata_gate"},
    }
    out = evidence_root() / "security" / "secret_rotation_metadata_gate.json"
    write_json_report(out, report)
    print(f"SECRET_ROTATION_METADATA_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
