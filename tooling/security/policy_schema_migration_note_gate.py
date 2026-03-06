#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
bootstrap_key = artifact_signing.bootstrap_key
current_key = artifact_signing.current_key
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

NOTES = ROOT / "governance" / "security" / "policy_schema_migration_notes.json"
SCHEMA_FILES = (
    ROOT / "governance" / "security" / "security_report_schema_contract.json",
    ROOT / "governance" / "security" / "security_event_schema.json",
    ROOT / "governance" / "security" / "security_schema_compatibility_policy.json",
)


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_iso(text: str) -> datetime | None:
    raw = str(text).strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _verify_notes_signature(notes_path: Path) -> tuple[bool, str]:
    sig_path = notes_path.with_suffix(".json.sig")
    if not sig_path.exists():
        return False, "missing_schema_migration_notes_signature"
    signature = sig_path.read_text(encoding="utf-8").strip()
    if not signature:
        return False, "empty_schema_migration_notes_signature"
    try:
        key = current_key(strict=False)
    except Exception as exc:
        key = None
        err = str(exc)
    else:
        err = ""
    if key is not None and verify_file(notes_path, signature, key=key):
        return True, "ok"
    if verify_file(notes_path, signature, key=bootstrap_key()):
        return True, "ok_bootstrap_key"
    if err:
        return False, f"schema_migration_notes_signature_verification_error:{err}"
    return False, "invalid_schema_migration_notes_signature"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []
    if not NOTES.exists():
        findings.append("missing_policy_schema_migration_notes")
        notes_payload: dict[str, Any] = {}
    else:
        ok, reason = _verify_notes_signature(NOTES)
        if not ok:
            findings.append(reason)
        payload = json.loads(NOTES.read_text(encoding="utf-8"))
        notes_payload = payload if isinstance(payload, dict) else {}

    if str(notes_payload.get("schema_version", "")).strip() != "glyphser-policy-schema-migration-notes.v1":
        findings.append("invalid_policy_schema_migration_notes_schema_version")

    raw_entries = notes_payload.get("entries", [])
    entries = [item for item in raw_entries if isinstance(item, dict)] if isinstance(raw_entries, list) else []

    by_path: dict[str, dict[str, Any]] = {}
    for idx, entry in enumerate(entries):
        rel = str(entry.get("path", "")).strip()
        if not rel:
            findings.append(f"invalid_note_path:{idx}")
            continue
        by_path[rel] = entry

    covered = 0
    for schema_path in SCHEMA_FILES:
        rel = str(schema_path.relative_to(ROOT)).replace("\\", "/")
        if not schema_path.exists():
            findings.append(f"missing_schema_file:{rel}")
            continue
        expected_sha = _sha256_file(schema_path)
        entry = by_path.get(rel)
        if entry is None:
            findings.append(f"missing_migration_note_entry:{rel}")
            continue
        covered += 1
        note = str(entry.get("note", "")).strip()
        updated_utc = _parse_iso(entry.get("updated_utc", ""))
        entry_sha = str(entry.get("sha256", "")).strip().lower()
        if not note:
            findings.append(f"missing_migration_note_text:{rel}")
        if updated_utc is None:
            findings.append(f"invalid_migration_note_updated_utc:{rel}")
        if entry_sha != expected_sha:
            findings.append(f"schema_hash_mismatch_requires_note_refresh:{rel}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"schema_files": len(SCHEMA_FILES), "covered_entries": covered, "note_entries": len(entries)},
        "metadata": {"gate": "policy_schema_migration_note_gate"},
    }
    out = evidence_root() / "security" / "policy_schema_migration_note_gate.json"
    write_json_report(out, report)
    print(f"POLICY_SCHEMA_MIGRATION_NOTE_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
