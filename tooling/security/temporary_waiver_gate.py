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
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    policy = json.loads((ROOT / "governance" / "security" / "temporary_waiver_policy.json").read_text(encoding="utf-8"))
    max_active = int(policy.get("max_active_waivers", 5))
    max_per_family = int(policy.get("max_active_waivers_per_control_family", 0))
    required = [f for f in policy.get("required_fields", []) if isinstance(f, str)]
    glob_pattern = str(policy.get("waiver_file_glob", "**/waivers.json")).strip() or "**/waivers.json"
    if glob_pattern.startswith("evidence/"):
        glob_pattern = glob_pattern[len("evidence/") :]
    evidence_base = evidence_root()
    findings: list[str] = []
    active_count = 0
    active_count_by_control_family: dict[str, int] = {}
    now = datetime.now(UTC)

    for path in sorted(evidence_base.glob(glob_pattern)):
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
                if max_per_family > 0:
                    control_family = str(w.get("control_family", "")).strip()
                    if not control_family:
                        findings.append(f"missing_waiver_control_family:{path}")
                    else:
                        active_count_by_control_family[control_family] = (
                            active_count_by_control_family.get(control_family, 0) + 1
                        )

    if active_count > max_active:
        findings.append(f"active_waivers_exceed_limit:{active_count}")
    if max_per_family > 0:
        for control_family, count in sorted(active_count_by_control_family.items()):
            if count > max_per_family:
                findings.append(f"active_waivers_exceed_control_family_limit:{control_family}:{count}:{max_per_family}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "active_waivers": active_count,
            "max_active_waivers": max_active,
            "max_active_waivers_per_control_family": max_per_family,
            "active_waivers_by_control_family": active_count_by_control_family,
        },
        "metadata": {"gate": "temporary_waiver_gate"},
    }
    out = evidence_root() / "security" / "temporary_waiver_gate.json"
    write_json_report(out, report)
    print(f"TEMPORARY_WAIVER_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
