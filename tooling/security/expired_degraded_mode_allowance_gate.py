#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(str(text).replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def _is_active(entry: dict[str, object]) -> bool:
    raw = entry.get("active", True)
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, str):
        return raw.strip().lower() not in {"false", "0", "no", "off", "inactive", "closed"}
    if isinstance(raw, int):
        return raw != 0
    return bool(raw)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy_path = ROOT / "governance" / "security" / "temporary_waiver_policy.json"
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    glob_pattern = str(policy.get("waiver_file_glob", "**/waivers.json")).strip() or "**/waivers.json"
    if glob_pattern.startswith("evidence/"):
        glob_pattern = glob_pattern[len("evidence/") :]

    findings: list[str] = []
    checked_waivers = 0
    expired_active = 0
    now = datetime.now(UTC)
    evidence_base = evidence_root()

    for path in sorted(evidence_base.glob(glob_pattern)):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            findings.append(f"invalid_waiver_json:{path}")
            continue
        waivers = payload.get("waivers", []) if isinstance(payload, dict) else []
        if not isinstance(waivers, list):
            findings.append(f"invalid_waiver_list:{path}")
            continue
        for idx, waiver in enumerate(waivers):
            if not isinstance(waiver, dict):
                findings.append(f"invalid_waiver_entry:{path}:{idx}")
                continue
            checked_waivers += 1
            exp = _parse_ts(waiver.get("expires_at_utc", ""))
            if exp is None:
                findings.append(f"invalid_waiver_expiry:{path}:{idx}")
                continue
            if exp <= now and _is_active(waiver):
                waiver_id = str(waiver.get("id", f"idx-{idx}")).strip() or f"idx-{idx}"
                findings.append(f"expired_active_degraded_allowance:{waiver_id}:{path}")
                expired_active += 1

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "waivers_checked": checked_waivers,
            "expired_active_allowances": expired_active,
            "waiver_policy_path": str(policy_path.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "expired_degraded_mode_allowance_gate"},
    }
    out = evidence_root() / "security" / "expired_degraded_mode_allowance_gate.json"
    write_json_report(out, report)
    print(f"EXPIRED_DEGRADED_MODE_ALLOWANCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
