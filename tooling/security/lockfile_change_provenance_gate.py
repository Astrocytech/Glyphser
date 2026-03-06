#!/usr/bin/env python3
from __future__ import annotations

import hashlib
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

LOCKFILE_PATH = ROOT / "requirements.lock"
APPROVAL_FILE = ROOT / "governance" / "security" / "lockfile_change_approval.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _changed_files() -> list[str]:
    proc = run_checked(["git", "diff", "--name-only", "HEAD~1", "HEAD", "--", "."])
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _lockfile_changed() -> bool:
    lock_rel = str(LOCKFILE_PATH.relative_to(ROOT)).replace("\\", "/")
    proc = run_checked(["git", "diff", "--name-only", "HEAD~1", "HEAD", "--", lock_rel])
    if proc.returncode != 0:
        return False
    return any(line.strip() == lock_rel for line in proc.stdout.splitlines())


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    changed = _changed_files()
    lockfile_changed = _lockfile_changed()

    approval_rel = str(APPROVAL_FILE.relative_to(ROOT)).replace("\\", "/")
    sig_rel = str(APPROVAL_FILE.with_suffix(".json.sig").relative_to(ROOT)).replace("\\", "/")
    lock_rel = str(LOCKFILE_PATH.relative_to(ROOT)).replace("\\", "/")

    if lockfile_changed:
        if approval_rel not in changed:
            findings.append("missing_updated_lockfile_change_approval_file")
        if sig_rel not in changed:
            findings.append("missing_updated_lockfile_change_approval_signature")
        if not APPROVAL_FILE.exists():
            findings.append("missing_lockfile_change_approval_file")
        else:
            payload = json.loads(APPROVAL_FILE.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                findings.append("invalid_lockfile_change_approval_file")
            else:
                for field in ("ticket", "rationale", "approved_by", "approved_at_utc", "expires_at_utc", "lockfile_sha256"):
                    if not str(payload.get(field, "")).strip():
                        findings.append(f"missing_lockfile_change_approval_field:{field}")
                approved_at = _parse_ts(str(payload.get("approved_at_utc", "")))
                expires_at = _parse_ts(str(payload.get("expires_at_utc", "")))
                now = datetime.now(UTC)
                if approved_at is None:
                    findings.append("invalid_lockfile_change_approved_at")
                if expires_at is None:
                    findings.append("invalid_lockfile_change_expires_at")
                if approved_at and expires_at and approved_at > expires_at:
                    findings.append("lockfile_change_approval_time_range_invalid")
                if expires_at and expires_at < now:
                    findings.append("lockfile_change_approval_expired")
                if LOCKFILE_PATH.exists():
                    lock_sha = _sha256(LOCKFILE_PATH)
                    if str(payload.get("lockfile_sha256", "")).strip().lower() != lock_sha.lower():
                        findings.append("lockfile_change_approval_hash_mismatch")
                else:
                    findings.append("lockfile_missing")

            sig = APPROVAL_FILE.with_suffix(".json.sig")
            if not sig.exists():
                findings.append("missing_lockfile_change_approval_signature")
            else:
                key = artifact_signing.current_key(strict=False)
                signature = sig.read_text(encoding="utf-8").strip()
                if not artifact_signing.verify_file(APPROVAL_FILE, signature, key=key):
                    findings.append("invalid_lockfile_change_approval_signature")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "lockfile_changed": lockfile_changed,
            "changed_files_count": len(changed),
            "lockfile_path": lock_rel,
            "approval_file": approval_rel,
        },
        "metadata": {"gate": "lockfile_change_provenance_gate"},
    }
    out = evidence_root() / "security" / "lockfile_change_provenance_gate.json"
    write_json_report(out, report)
    print(f"LOCKFILE_CHANGE_PROVENANCE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
