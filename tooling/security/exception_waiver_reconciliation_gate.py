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
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

EXCEPTIONS_FILE = ROOT / "governance" / "security" / "temporary_exceptions.json"
WAIVER_POLICY = ROOT / "governance" / "security" / "temporary_waiver_policy.json"


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def _expired_waiver_ids(base: Path, glob_pattern: str) -> set[str]:
    if glob_pattern.startswith("evidence/"):
        glob_pattern = glob_pattern[len("evidence/") :]
    expired: set[str] = set()
    now = datetime.now(UTC)
    for path in sorted(base.glob(glob_pattern)):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        waivers = payload.get("waivers", []) if isinstance(payload, dict) else []
        if not isinstance(waivers, list):
            continue
        for w in waivers:
            if not isinstance(w, dict):
                continue
            wid = str(w.get("id", "")).strip()
            exp = _parse_ts(str(w.get("expires_at_utc", "")))
            if wid and exp and exp < now:
                expired.add(wid)
    return expired


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    policy = json.loads(WAIVER_POLICY.read_text(encoding="utf-8"))
    if not isinstance(policy, dict):
        raise ValueError("invalid temporary waiver policy")
    glob_pattern = str(policy.get("waiver_file_glob", "**/waivers.json")).strip() or "**/waivers.json"
    expired_ids = _expired_waiver_ids(evidence_root(), glob_pattern)

    exceptions_payload: dict[str, Any] = {}
    if EXCEPTIONS_FILE.exists():
        loaded = json.loads(EXCEPTIONS_FILE.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            exceptions_payload = loaded
    closed_raw = exceptions_payload.get("closed_waivers", [])
    closed_ids = {
        str(item.get("id", "")).strip()
        for item in closed_raw
        if isinstance(item, dict) and str(item.get("id", "")).strip()
    }

    missing_closures = sorted(wid for wid in expired_ids if wid not in closed_ids)
    for wid in missing_closures:
        findings.append(f"expired_waiver_missing_closure:{wid}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "expired_waivers_detected": len(expired_ids),
            "closed_waivers_recorded": len(closed_ids),
            "missing_closures": len(missing_closures),
        },
        "metadata": {"gate": "exception_waiver_reconciliation_gate"},
    }
    out = evidence_root() / "security" / "exception_waiver_reconciliation_gate.json"
    write_json_report(out, report)
    sig = artifact_signing.sign_file(out, key=artifact_signing.current_key(strict=False))
    out.with_suffix(".json.sig").write_text(sig + "\n", encoding="utf-8")
    print(f"EXCEPTION_WAIVER_RECONCILIATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
