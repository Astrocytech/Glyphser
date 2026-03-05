from __future__ import annotations

import hashlib
import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import lockfile_change_provenance_gate


def _write_approval(repo: Path, *, lock_sha: str) -> None:
    approval = repo / "governance" / "security" / "lockfile_change_approval.json"
    approval.parent.mkdir(parents=True, exist_ok=True)
    approval.write_text(
        json.dumps(
            {
                "ticket": "SEC-456",
                "rationale": "Lockfile refresh approved after vulnerability triage.",
                "approved_by": "security-ops",
                "approved_at_utc": "2026-03-01T00:00:00+00:00",
                "expires_at_utc": "2099-01-01T00:00:00+00:00",
                "lockfile_sha256": lock_sha,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    approval.with_suffix(".json.sig").write_text(sign_file(approval, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_lockfile_change_provenance_gate_skips_when_lockfile_unchanged(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(lockfile_change_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(lockfile_change_provenance_gate, "LOCKFILE_PATH", repo / "requirements.lock")
    monkeypatch.setattr(
        lockfile_change_provenance_gate,
        "APPROVAL_FILE",
        repo / "governance" / "security" / "lockfile_change_approval.json",
    )
    monkeypatch.setattr(lockfile_change_provenance_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(lockfile_change_provenance_gate, "_lockfile_changed", lambda: False)
    monkeypatch.setattr(lockfile_change_provenance_gate, "_changed_files", lambda: [])
    assert lockfile_change_provenance_gate.main([]) == 0


def test_lockfile_change_provenance_gate_fails_without_signed_approval(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "requirements.lock").write_text("pytest==8.3.3\n", encoding="utf-8")
    monkeypatch.setattr(lockfile_change_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(lockfile_change_provenance_gate, "LOCKFILE_PATH", repo / "requirements.lock")
    monkeypatch.setattr(
        lockfile_change_provenance_gate,
        "APPROVAL_FILE",
        repo / "governance" / "security" / "lockfile_change_approval.json",
    )
    monkeypatch.setattr(lockfile_change_provenance_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(lockfile_change_provenance_gate, "_lockfile_changed", lambda: True)
    monkeypatch.setattr(lockfile_change_provenance_gate, "_changed_files", lambda: ["requirements.lock"])
    assert lockfile_change_provenance_gate.main([]) == 1


def test_lockfile_change_provenance_gate_passes_with_signed_matching_hash(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True, exist_ok=True)
    lock = repo / "requirements.lock"
    lock.write_text("pytest==8.3.3\n", encoding="utf-8")
    lock_sha = hashlib.sha256(lock.read_bytes()).hexdigest()
    _write_approval(repo, lock_sha=lock_sha)

    monkeypatch.setattr(lockfile_change_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(lockfile_change_provenance_gate, "LOCKFILE_PATH", lock)
    monkeypatch.setattr(
        lockfile_change_provenance_gate,
        "APPROVAL_FILE",
        repo / "governance" / "security" / "lockfile_change_approval.json",
    )
    monkeypatch.setattr(lockfile_change_provenance_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(lockfile_change_provenance_gate, "_lockfile_changed", lambda: True)
    monkeypatch.setattr(
        lockfile_change_provenance_gate,
        "_changed_files",
        lambda: [
            "requirements.lock",
            "governance/security/lockfile_change_approval.json",
            "governance/security/lockfile_change_approval.json.sig",
        ],
    )
    assert lockfile_change_provenance_gate.main([]) == 0
