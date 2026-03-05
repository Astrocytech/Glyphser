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

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
run_checked = importlib.import_module("tooling.security.subprocess_policy").run_checked
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

RULE_FILES = [
    "tooling/security/semgrep-rules.yml",
    "tooling/security/bandit.yaml",
]
APPROVAL_FILE = ROOT / "governance" / "security" / "security_rule_diff_approval.json"


def _changed_files() -> list[str]:
    proc = run_checked(["git", "diff", "--name-only", "HEAD~1", "HEAD", "--", "."])
    if proc.returncode != 0:
        return []
    return [line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _rules_diff() -> str:
    proc = run_checked(["git", "diff", "--unified=0", "HEAD~1", "HEAD", "--", *RULE_FILES], cwd=ROOT)
    if proc.returncode != 0:
        return ""
    return proc.stdout


def _parse_ts(text: str) -> datetime | None:
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
        return dt if dt.tzinfo else dt.replace(tzinfo=UTC)
    except Exception:
        return None


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    diff_text = _rules_diff()
    changed = _changed_files()
    has_changes = bool(diff_text.strip())
    diff_sha = hashlib.sha256(diff_text.encode("utf-8")).hexdigest()

    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "security_rule_baseline_diff.txt").write_text(diff_text, encoding="utf-8")

    if has_changes:
        approval_rel = str(APPROVAL_FILE.relative_to(ROOT)).replace("\\", "/")
        sig_rel = str(APPROVAL_FILE.with_suffix(".json.sig").relative_to(ROOT)).replace("\\", "/")
        if approval_rel not in changed:
            findings.append("missing_updated_security_rule_diff_approval_file")
        if sig_rel not in changed:
            findings.append("missing_updated_security_rule_diff_approval_signature")

        if not APPROVAL_FILE.exists():
            findings.append("missing_security_rule_diff_approval_file")
        else:
            payload = json.loads(APPROVAL_FILE.read_text(encoding="utf-8"))
            if not isinstance(payload, dict):
                findings.append("invalid_security_rule_diff_approval_file")
            else:
                for field in ("ticket", "rationale", "approved_by", "approved_at_utc", "expires_at_utc", "rule_diff_sha256"):
                    if not str(payload.get(field, "")).strip():
                        findings.append(f"missing_security_rule_diff_approval_field:{field}")
                approved_at = _parse_ts(str(payload.get("approved_at_utc", "")))
                expires_at = _parse_ts(str(payload.get("expires_at_utc", "")))
                now = datetime.now(UTC)
                if approved_at is None:
                    findings.append("invalid_security_rule_diff_approved_at")
                if expires_at is None:
                    findings.append("invalid_security_rule_diff_expires_at")
                if approved_at and expires_at and approved_at > expires_at:
                    findings.append("security_rule_diff_approval_time_range_invalid")
                if expires_at and expires_at < now:
                    findings.append("security_rule_diff_approval_expired")
                if str(payload.get("rule_diff_sha256", "")).strip() != diff_sha:
                    findings.append("security_rule_diff_hash_mismatch")

            sig = APPROVAL_FILE.with_suffix(".json.sig")
            if not sig.exists():
                findings.append("missing_security_rule_diff_approval_signature")
            else:
                sig_text = sig.read_text(encoding="utf-8").strip()
                key = artifact_signing.current_key(strict=False)
                verified = artifact_signing.verify_file(APPROVAL_FILE, sig_text, key=key)
                if not verified:
                    verified = artifact_signing.verify_file(APPROVAL_FILE, sig_text, key=artifact_signing.bootstrap_key())
                if not verified:
                    findings.append("invalid_security_rule_diff_approval_signature")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "rule_files": RULE_FILES,
            "rules_changed": has_changes,
            "rules_diff_sha256": diff_sha,
            "changed_files_count": len(changed),
            "approval_file": str(APPROVAL_FILE.relative_to(ROOT)).replace("\\", "/"),
        },
        "metadata": {"gate": "security_rule_baseline_gate"},
    }
    out = sec / "security_rule_baseline_gate.json"
    write_json_report(out, report)
    print(f"SECURITY_RULE_BASELINE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
