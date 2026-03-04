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


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads((ROOT / "governance" / "security" / "temporary_waiver_policy.json").read_text(encoding="utf-8"))
    max_active = int(policy.get("max_active_waivers", 5))
    required = [f for f in policy.get("required_fields", []) if isinstance(f, str)]
    findings: list[str] = []
    active_count = 0
    now = datetime.now(UTC)

    for path in sorted(ROOT.glob("evidence/**/waivers.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_json:{path}")
            continue
        waivers = payload.get("waivers", []) if isinstance(payload, dict) else []
        if not isinstance(waivers, list):
            findings.append(f"invalid_waiver_list:{path}")
            continue
        for w in waivers:
            if not isinstance(w, dict):
                findings.append(f"invalid_waiver_entry:{path}")
                continue
            for field in required:
                if field not in w:
                    findings.append(f"missing_waiver_field:{field}:{path}")
            exp = _parse_ts(str(w.get("expires_at_utc", "")))
            if exp is None:
                findings.append(f"invalid_waiver_expiry:{path}")
                continue
            if exp < now:
                findings.append(f"expired_waiver:{path}")
            else:
                active_count += 1

    if active_count > max_active:
        findings.append(f"active_waivers_exceed_limit:{active_count}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"active_waivers": active_count, "max_active_waivers": max_active},
        "metadata": {"gate": "temporary_waiver_gate"},
    }
    out = evidence_root() / "security" / "temporary_waiver_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"TEMPORARY_WAIVER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
