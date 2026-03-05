from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import file_mode_change_gate


def _write_approval(repo: Path, approved_mode_changes: list[dict[str, str]]) -> None:
    approval = repo / "governance" / "security" / "file_mode_change_approval.json"
    approval.parent.mkdir(parents=True, exist_ok=True)
    approval.write_text(
        json.dumps(
            {
                "ticket": "SEC-456",
                "rationale": "Reviewed mode transition for intentional script chmod.",
                "approved_by": "security-ops",
                "approved_at_utc": "2026-03-01T00:00:00+00:00",
                "expires_at_utc": "2099-01-01T00:00:00+00:00",
                "approved_mode_changes": approved_mode_changes,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    approval.with_suffix(".json.sig").write_text(
        sign_file(approval, key=current_key(strict=False)) + "\n",
        encoding="utf-8",
    )


def test_file_mode_change_gate_skips_when_no_mode_change(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(file_mode_change_gate, "ROOT", repo)
    monkeypatch.setattr(
        file_mode_change_gate,
        "APPROVAL_FILE",
        repo / "governance/security/file_mode_change_approval.json",
    )
    monkeypatch.setattr(file_mode_change_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(file_mode_change_gate, "_mode_changes", lambda: [])
    monkeypatch.setattr(file_mode_change_gate, "_changed_files", lambda: [])
    assert file_mode_change_gate.main([]) == 0


def test_file_mode_change_gate_fails_without_valid_approval(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(file_mode_change_gate, "ROOT", repo)
    monkeypatch.setattr(
        file_mode_change_gate,
        "APPROVAL_FILE",
        repo / "governance/security/file_mode_change_approval.json",
    )
    monkeypatch.setattr(file_mode_change_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        file_mode_change_gate,
        "_mode_changes",
        lambda: [{"path": "tooling/security/foo.py", "old_mode": "100644", "new_mode": "100755"}],
    )
    monkeypatch.setattr(file_mode_change_gate, "_changed_files", lambda: ["tooling/security/foo.py"])
    assert file_mode_change_gate.main([]) == 1


def test_file_mode_change_gate_passes_with_signed_approval(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_approval(
        repo,
        [{"path": "tooling/security/foo.py", "old_mode": "100644", "new_mode": "100755"}],
    )
    monkeypatch.setattr(file_mode_change_gate, "ROOT", repo)
    monkeypatch.setattr(
        file_mode_change_gate,
        "APPROVAL_FILE",
        repo / "governance/security/file_mode_change_approval.json",
    )
    monkeypatch.setattr(file_mode_change_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        file_mode_change_gate,
        "_mode_changes",
        lambda: [{"path": "tooling/security/foo.py", "old_mode": "100644", "new_mode": "100755"}],
    )
    monkeypatch.setattr(
        file_mode_change_gate,
        "_changed_files",
        lambda: [
            "tooling/security/foo.py",
            "governance/security/file_mode_change_approval.json",
            "governance/security/file_mode_change_approval.json.sig",
        ],
    )
    assert file_mode_change_gate.main([]) == 0
