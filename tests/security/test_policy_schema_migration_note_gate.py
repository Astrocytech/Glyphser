from __future__ import annotations

import hashlib
import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import bootstrap_key, sign_file
from tooling.security import policy_schema_migration_note_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=bootstrap_key()) + "\n", encoding="utf-8")


def _seed_schema_files(sec: Path) -> tuple[Path, Path, Path]:
    a = sec / "security_report_schema_contract.json"
    b = sec / "security_event_schema.json"
    c = sec / "security_schema_compatibility_policy.json"
    _write(a, {"schema_version": "1.0"})
    _write(b, {"$id": "security-event-schema"})
    _write(c, {"current_schema_version": 1})
    return a, b, c


def test_policy_schema_migration_note_gate_passes_with_matching_hashes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "governance" / "security"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)
    a, b, c = _seed_schema_files(sec)

    notes = sec / "policy_schema_migration_notes.json"
    _write(
        notes,
        {
            "schema_version": "glyphser-policy-schema-migration-notes.v1",
            "entries": [
                {"path": "governance/security/security_report_schema_contract.json", "sha256": _sha(a), "updated_utc": "2026-03-06T00:00:00+00:00", "note": "ok"},
                {"path": "governance/security/security_event_schema.json", "sha256": _sha(b), "updated_utc": "2026-03-06T00:00:00+00:00", "note": "ok"},
                {"path": "governance/security/security_schema_compatibility_policy.json", "sha256": _sha(c), "updated_utc": "2026-03-06T00:00:00+00:00", "note": "ok"},
            ],
        },
    )
    _sign(notes)

    monkeypatch.setattr(policy_schema_migration_note_gate, "ROOT", repo)
    monkeypatch.setattr(policy_schema_migration_note_gate, "NOTES", notes)
    monkeypatch.setattr(policy_schema_migration_note_gate, "SCHEMA_FILES", (a, b, c))
    monkeypatch.setattr(policy_schema_migration_note_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_schema_migration_note_gate.main([]) == 0


def test_policy_schema_migration_note_gate_fails_when_hash_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "governance" / "security"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)
    a, b, c = _seed_schema_files(sec)

    notes = sec / "policy_schema_migration_notes.json"
    _write(
        notes,
        {
            "schema_version": "glyphser-policy-schema-migration-notes.v1",
            "entries": [
                {"path": "governance/security/security_report_schema_contract.json", "sha256": "deadbeef", "updated_utc": "2026-03-06T00:00:00+00:00", "note": "stale"},
                {"path": "governance/security/security_event_schema.json", "sha256": _sha(b), "updated_utc": "2026-03-06T00:00:00+00:00", "note": "ok"},
                {"path": "governance/security/security_schema_compatibility_policy.json", "sha256": _sha(c), "updated_utc": "2026-03-06T00:00:00+00:00", "note": "ok"},
            ],
        },
    )
    _sign(notes)

    monkeypatch.setattr(policy_schema_migration_note_gate, "ROOT", repo)
    monkeypatch.setattr(policy_schema_migration_note_gate, "NOTES", notes)
    monkeypatch.setattr(policy_schema_migration_note_gate, "SCHEMA_FILES", (a, b, c))
    monkeypatch.setattr(policy_schema_migration_note_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_schema_migration_note_gate.main([]) == 1
    report = json.loads((ev / "policy_schema_migration_note_gate.json").read_text(encoding="utf-8"))
    assert "schema_hash_mismatch_requires_note_refresh:governance/security/security_report_schema_contract.json" in report["findings"]
