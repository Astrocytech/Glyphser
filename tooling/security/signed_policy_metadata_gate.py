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


def _parse_iso(ts: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    manifest_path = ROOT / "governance" / "security" / "policy_signature_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    policies = manifest.get("policies", []) if isinstance(manifest, dict) else []
    if not isinstance(policies, list):
        raise ValueError("invalid policy signature manifest")

    findings: list[str] = []
    checked = 0
    for rel in policies:
        if not isinstance(rel, str):
            findings.append("invalid_manifest_entry")
            continue
        path = ROOT / rel
        if not path.exists():
            findings.append(f"missing_policy:{rel}")
            continue
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
        checked += 1
        if not isinstance(payload, dict):
            findings.append(f"invalid_policy_object:{rel}")
            continue
        owner = str(payload.get("owner", "")).strip()
        if not owner:
            findings.append(f"missing_owner:{rel}")
        reviewed_raw = str(payload.get("last_reviewed_utc", "")).strip()
        if not reviewed_raw:
            findings.append(f"missing_last_reviewed_utc:{rel}")
        elif _parse_iso(reviewed_raw) is None:
            findings.append(f"invalid_last_reviewed_utc:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"checked_policies": checked, "manifest_entries": len(policies)},
        "metadata": {"gate": "signed_policy_metadata_gate"},
    }
    out = evidence_root() / "security" / "signed_policy_metadata_gate.json"
    write_json_report(out, report)
    print(f"SIGNED_POLICY_METADATA_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
