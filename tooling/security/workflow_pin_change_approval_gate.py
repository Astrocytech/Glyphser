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
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

APPROVAL_FILE = ROOT / "governance" / "security" / "workflow_pin_change_approval.json"


def _changed_files() -> list[str]:
    proc = run_checked(["git", "diff", "--name-only", "HEAD~1", "HEAD", "--", "."])
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _pin_refs_changed() -> bool:
    proc = run_checked(["git", "diff", "--unified=0", "HEAD~1", "HEAD", "--", ".github/workflows"])
    if proc.returncode != 0:
        return False
    for raw in proc.stdout.splitlines():
        line = raw.strip()
        if not line or line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+") or line.startswith("-"):
            if "uses:" in line:
                return True
    return False


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    pin_changed = _pin_refs_changed()
    changed = _changed_files()
    skipped = not pin_changed

    if pin_changed:
        if str(APPROVAL_FILE.relative_to(ROOT)).replace("\\", "/") not in changed:
            findings.append("missing_updated_pin_change_approval_file")
        if str(APPROVAL_FILE.with_suffix(".json.sig").relative_to(ROOT)).replace("\\", "/") not in changed:
            findings.append("missing_updated_pin_change_approval_signature")
        if not APPROVAL_FILE.exists():
            findings.append("missing_pin_change_approval_file")
        else:
            payload = json.loads(APPROVAL_FILE.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                findings.append("invalid_pin_change_approval_file")
            else:
                for field in ("ticket", "rationale", "approved_by", "approved_at_utc", "expires_at_utc"):
                    if not str(payload.get(field, "")).strip():
                        findings.append(f"missing_pin_change_approval_field:{field}")
                approved_at = _parse_ts(str(payload.get("approved_at_utc", "")))
                expires_at = _parse_ts(str(payload.get("expires_at_utc", "")))
                now = datetime.now(UTC)
                if approved_at is None:
                    findings.append("invalid_pin_change_approved_at")
                if expires_at is None:
                    findings.append("invalid_pin_change_expires_at")
                if approved_at and expires_at and approved_at > expires_at:
                    findings.append("pin_change_approval_time_range_invalid")
                if expires_at and expires_at < now:
                    findings.append("pin_change_approval_expired")

            sig = APPROVAL_FILE.with_suffix(".json.sig")
            if not sig.exists():
                findings.append("missing_pin_change_approval_signature")
            else:
                key = artifact_signing.current_key(strict=False)
                if not artifact_signing.verify_file(APPROVAL_FILE, sig.read_text(encoding="utf-8").strip(), key=key):
                    findings.append("invalid_pin_change_approval_signature")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "pin_refs_changed": pin_changed,
            "skipped": skipped,
            "changed_files_count": len(changed),
            "approval_file": str(APPROVAL_FILE.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "workflow_pin_change_approval_gate"},
    }
    out = evidence_root() / "security" / "workflow_pin_change_approval_gate.json"
    write_json_report(out, report)
    print(f"WORKFLOW_PIN_CHANGE_APPROVAL_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
