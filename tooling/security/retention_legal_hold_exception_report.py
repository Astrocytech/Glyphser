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

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

EXCEPTIONS = ROOT / "governance" / "security" / "retention_legal_hold_exceptions.json"


def _parse_iso(value: str) -> datetime | None:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    sig = EXCEPTIONS.with_suffix(".json.sig")
    if not sig.exists():
        findings.append("missing_retention_legal_hold_exceptions_signature")
        payload: dict[str, object] = {"exceptions": []}
    else:
        sig_text = sig.read_text(encoding="utf-8").strip()
        if not artifact_signing.verify_file(EXCEPTIONS, sig_text, key=artifact_signing.current_key(strict=False)):
            if not artifact_signing.verify_file(EXCEPTIONS, sig_text, key=artifact_signing.bootstrap_key()):
                findings.append("invalid_retention_legal_hold_exceptions_signature")
        payload = json.loads(EXCEPTIONS.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            findings.append("invalid_retention_legal_hold_exceptions_payload")
            payload = {"exceptions": []}

    exceptions = payload.get("exceptions", []) if isinstance(payload.get("exceptions"), list) else []
    now = datetime.now(UTC)
    active = 0

    for idx, item in enumerate(exceptions):
        if not isinstance(item, dict):
            findings.append(f"invalid_exception_entry:{idx}")
            continue
        exception_id = str(item.get("exception_id", "")).strip()
        approved_by = str(item.get("approved_by", "")).strip()
        approval_ticket = str(item.get("approval_ticket", "")).strip()
        approved_at = _parse_iso(str(item.get("approved_at_utc", "")).strip())
        expires_at = _parse_iso(str(item.get("expires_at_utc", "")).strip())

        if not exception_id:
            findings.append(f"missing_exception_id:{idx}")
        if not approved_by:
            findings.append(f"missing_approved_by:{idx}")
        if not approval_ticket:
            findings.append(f"missing_approval_ticket:{idx}")
        if approved_at is None:
            findings.append(f"invalid_approved_at_utc:{idx}")
        if expires_at is None:
            findings.append(f"invalid_expires_at_utc:{idx}")
            continue
        if expires_at <= now:
            findings.append(f"expired_legal_hold_exception:{exception_id or idx}")
        else:
            active += 1

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "total_exceptions": len(exceptions),
            "active_exceptions": active,
        },
        "metadata": {"gate": "retention_legal_hold_exception_report"},
    }
    out = evidence_root() / "security" / "retention_legal_hold_exception_report.json"
    write_json_report(out, report)
    print(f"RETENTION_LEGAL_HOLD_EXCEPTION_REPORT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
