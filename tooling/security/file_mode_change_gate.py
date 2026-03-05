#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

APPROVAL_FILE = ROOT / "governance" / "security" / "file_mode_change_approval.json"
MONITORED_PATHS = [".github/workflows", "tooling/security"]
MODE_CHANGE_RE = re.compile(r"^mode change (\d+) => (\d+) (.+)$")


def _changed_files() -> list[str]:
    proc = run_checked(["git", "diff", "--name-only", "HEAD~1", "HEAD", "--", "."])
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _mode_changes() -> list[dict[str, str]]:
    proc = run_checked(["git", "diff", "--summary", "HEAD~1", "HEAD", "--", *MONITORED_PATHS])
    if proc.returncode != 0:
        return []
    changes: list[dict[str, str]] = []
    for raw in proc.stdout.splitlines():
        line = raw.strip()
        match = MODE_CHANGE_RE.match(line)
        if not match:
            continue
        changes.append({"old_mode": match.group(1), "new_mode": match.group(2), "path": match.group(3).strip()})
    return changes


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def _normalized_approved_mode_changes(payload: dict[str, object]) -> set[str]:
    rows = payload.get("approved_mode_changes", [])
    if not isinstance(rows, list):
        return set()
    out: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        path = str(row.get("path", "")).strip()
        old_mode = str(row.get("old_mode", "")).strip()
        new_mode = str(row.get("new_mode", "")).strip()
        if not path or not old_mode or not new_mode:
            continue
        out.add(f"{path}:{old_mode}:{new_mode}")
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    mode_changes = _mode_changes()
    changed = _changed_files()
    skipped = not mode_changes

    if mode_changes:
        approval_rel = str(APPROVAL_FILE.relative_to(ROOT)).replace("\\", "/")
        sig_rel = str(APPROVAL_FILE.with_suffix(".json.sig").relative_to(ROOT)).replace("\\", "/")
        if approval_rel not in changed:
            findings.append("missing_updated_file_mode_change_approval_file")
        if sig_rel not in changed:
            findings.append("missing_updated_file_mode_change_approval_signature")

        if not APPROVAL_FILE.exists():
            findings.append("missing_file_mode_change_approval_file")
        else:
            payload = json.loads(APPROVAL_FILE.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                findings.append("invalid_file_mode_change_approval_file")
            else:
                for field in ("ticket", "rationale", "approved_by", "approved_at_utc", "expires_at_utc"):
                    if not str(payload.get(field, "")).strip():
                        findings.append(f"missing_file_mode_change_approval_field:{field}")
                approved_at = _parse_ts(str(payload.get("approved_at_utc", "")))
                expires_at = _parse_ts(str(payload.get("expires_at_utc", "")))
                now = datetime.now(UTC)
                if approved_at is None:
                    findings.append("invalid_file_mode_change_approved_at")
                if expires_at is None:
                    findings.append("invalid_file_mode_change_expires_at")
                if approved_at and expires_at and approved_at > expires_at:
                    findings.append("file_mode_change_approval_time_range_invalid")
                if expires_at and expires_at < now:
                    findings.append("file_mode_change_approval_expired")

                observed = {
                    f"{row['path']}:{row['old_mode']}:{row['new_mode']}"
                    for row in mode_changes
                    if row.get("path") and row.get("old_mode") and row.get("new_mode")
                }
                approved = _normalized_approved_mode_changes(payload)
                for entry in sorted(observed - approved):
                    findings.append(f"unapproved_mode_change:{entry}")

            sig = APPROVAL_FILE.with_suffix(".json.sig")
            if not sig.exists():
                findings.append("missing_file_mode_change_approval_signature")
            else:
                key = artifact_signing.current_key(strict=False)
                if not artifact_signing.verify_file(APPROVAL_FILE, sig.read_text(encoding="utf-8").strip(), key=key):
                    findings.append("invalid_file_mode_change_approval_signature")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "mode_changes_detected": len(mode_changes),
            "changed_files_count": len(changed),
            "skipped": skipped,
            "approval_file": str(APPROVAL_FILE.relative_to(ROOT)).replace("\\", "/"),
            "monitored_paths": MONITORED_PATHS,
        },
        "metadata": {"gate": "file_mode_change_gate"},
    }
    out = evidence_root() / "security" / "file_mode_change_gate.json"
    write_json_report(out, report)
    print(f"FILE_MODE_CHANGE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
