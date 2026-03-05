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

REGISTRY = ROOT / "governance" / "security" / "policy_deprecation_registry.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _parse_dt(text: str) -> datetime | None:
    raw = str(text).strip()
    if not raw:
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    if not REGISTRY.exists():
        findings.append("missing_policy_deprecation_registry")
        entries: list[dict[str, Any]] = []
    else:
        try:
            payload = _load_json(REGISTRY)
        except Exception:
            payload = {}
            findings.append("invalid_policy_deprecation_registry")
        raw = payload.get("deprecations", []) if isinstance(payload, dict) else []
        entries = [item for item in raw if isinstance(item, dict)] if isinstance(raw, list) else []

    now = datetime.now(UTC)
    overdue = 0
    for idx, item in enumerate(entries, start=1):
        policy = str(item.get("policy", "")).strip()
        sunset = _parse_dt(item.get("sunset_date_utc", ""))
        replacements = item.get("replacement_controls", [])
        evidence = item.get("migration_evidence", [])

        if not policy:
            findings.append(f"missing_policy:{idx}")
        if sunset is None:
            findings.append(f"invalid_sunset_date:{idx}")
        if not isinstance(replacements, list) or not [x for x in replacements if isinstance(x, str) and x.strip()]:
            findings.append(f"missing_replacement_controls:{idx}")

        if sunset is not None and sunset <= now:
            overdue += 1
            if not isinstance(evidence, list) or not [x for x in evidence if isinstance(x, str) and x.strip()]:
                findings.append(f"missing_migration_evidence_post_sunset:{policy or idx}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "deprecation_entries": len(entries),
            "overdue_entries": overdue,
            "registry_path": str(REGISTRY.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "policy_deprecation_gate"},
    }
    out = evidence_root() / "security" / "policy_deprecation_gate.json"
    write_json_report(out, report)
    print(f"POLICY_DEPRECATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
