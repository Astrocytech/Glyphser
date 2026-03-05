#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report
clock_consistency_violation = importlib.import_module("tooling.security.report_io").clock_consistency_violation

GOV_SECURITY_DIR = ROOT / "governance" / "security"
METADATA_DIR = GOV_SECURITY_DIR / "metadata"


def _parse_iso(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    max_age_days = int(os.environ.get("GLYPHSER_POLICY_REVIEW_MAX_AGE_DAYS", "90") or "90")
    strict_missing_metadata = os.environ.get("GLYPHSER_POLICY_REVIEW_REQUIRE_METADATA", "true").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    now = datetime.now(UTC)
    findings: list[str] = []
    checked = 0
    stale = 0
    missing_meta = 0
    clock_issue = clock_consistency_violation(now)
    if clock_issue:
        findings.append(clock_issue)

    for path in sorted(GOV_SECURITY_DIR.glob("*")):
        if not path.is_file():
            continue
        if path.suffix != ".md":
            continue
        if path.name.endswith(".sig"):
            continue
        checked += 1
        meta = METADATA_DIR / f"{path.stem}.meta.json"
        if not meta.exists():
            missing_meta += 1
            if strict_missing_metadata:
                findings.append(f"missing_metadata:{path.name}")
            continue
        sig = meta.with_suffix(".json.sig")
        if not sig.exists():
            findings.append(f"missing_metadata_signature:{meta.name}")
            continue
        sig_text = sig.read_text(encoding="utf-8").strip()
        if not sig_text:
            findings.append(f"empty_metadata_signature:{meta.name}")
            continue
        key = artifact_signing.current_key(strict=False)
        if not artifact_signing.verify_file(meta, sig_text, key=key):
            if not artifact_signing.verify_file(meta, sig_text, key=artifact_signing.bootstrap_key()):
                findings.append(f"invalid_metadata_signature:{meta.name}")
                continue
        payload = json.loads(meta.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            findings.append(f"invalid_metadata:{meta.name}")
            continue
        reviewed = _parse_iso(str(payload.get("last_reviewed_utc", "")).strip())
        if reviewed is None:
            findings.append(f"invalid_last_reviewed_utc:{meta.name}")
            continue
        age = now - reviewed
        if age > timedelta(days=max_age_days):
            stale += 1
            findings.append(f"stale_review:{path.name}:age_days:{age.days}:max_days:{max_age_days}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "checked_artifacts": checked,
            "missing_metadata": missing_meta,
            "stale_items": stale,
            "max_age_days": max_age_days,
            "strict_missing_metadata": strict_missing_metadata,
        },
        "metadata": {"gate": "policy_review_freshness_gate"},
    }
    out = evidence_root() / "security" / "policy_review_freshness_gate.json"
    write_json_report(out, report)
    print(f"POLICY_REVIEW_FRESHNESS_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
