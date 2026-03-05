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

INVENTORY = ROOT / "governance" / "security" / "secret_origin_inventory.json"
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
    names: set[str] = set()
    for path in (SECRET_POLICY, ORG_POLICY):
        payload = _load_json(path)
        required = payload.get("required_secrets", [])
        if isinstance(required, list):
            for item in required:
                if isinstance(item, str) and item.strip():
                    names.add(item.strip())
    return sorted(names)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not INVENTORY.exists():
        raise ValueError("missing governance/security/secret_origin_inventory.json")
    inventory = _load_json(INVENTORY)

    max_age = int(inventory.get("maximum_recertification_age_days", 90))
    secrets = inventory.get("secrets", [])
    if not isinstance(secrets, list):
        raise ValueError("secrets must be a list")

    by_name: dict[str, dict[str, Any]] = {}
    for entry in secrets:
        if not isinstance(entry, dict):
            findings.append("invalid_secret_entry")
            continue
        name = str(entry.get("name", "")).strip()
        if not name:
            findings.append("secret_missing_name")
            continue
        by_name[name] = entry

    required = _required_secret_names()
    missing_required = [name for name in required if name not in by_name]
    if missing_required:
        findings.append(f"missing_required_secret_inventory:{','.join(missing_required)}")

    for name, entry in sorted(by_name.items()):
        who = str(entry.get("provisioned_by", "")).strip()
        where = str(entry.get("provisioning_source", "")).strip()
        how = str(entry.get("provisioning_method", "")).strip()
        if not who:
            findings.append(f"{name}:missing_provisioned_by")
        if not where:
            findings.append(f"{name}:missing_provisioning_source")
        if not how:
            findings.append(f"{name}:missing_provisioning_method")

        recertified = str(entry.get("last_recertified_utc", "")).strip()
        interval_days = int(entry.get("recertification_interval_days", max_age))
        if interval_days <= 0:
            findings.append(f"{name}:invalid_recertification_interval_days")
            continue
        if not recertified:
            findings.append(f"{name}:missing_last_recertified_utc")
            continue
        try:
            age = _age_days(recertified)
        except ValueError:
            findings.append(f"{name}:invalid_last_recertified_utc")
            continue
        max_allowed = min(max_age, interval_days)
        if age > max_allowed:
            findings.append(f"{name}:recertification_stale:{age}>{max_allowed}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "required_secret_count": len(required),
            "inventory_secret_count": len(by_name),
            "missing_required_secret_count": len(missing_required),
            "maximum_recertification_age_days": max_age,
        },
        "metadata": {"gate": "secret_origin_inventory_gate"},
    }
    out = evidence_root() / "security" / "secret_origin_inventory_gate.json"
    write_json_report(out, report)
    print(f"SECRET_ORIGIN_INVENTORY_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
