from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_standards_profile_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_security_standards_profile_gate_passes_with_valid_profile(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(
        repo / "governance" / "security" / "security_standards_profile.json",
        {
            "profile_name": "glyphser-v1",
            "owner": "security",
            "reviewed_at_utc": "2026-03-05T00:00:00+00:00",
            "consumer_repos": ["a"],
            "required_controls": ["x"],
            "reference_templates": [".github/workflows/security-maintenance.yml"],
        },
    )
    monkeypatch.setattr(security_standards_profile_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_standards_profile_gate, "PROFILE", repo / "governance" / "security" / "security_standards_profile.json"
    )
    monkeypatch.setattr(security_standards_profile_gate, "evidence_root", lambda: ev)
    assert security_standards_profile_gate.main([]) == 0


def test_security_standards_profile_gate_fails_with_missing_required_fields(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(repo / "governance" / "security" / "security_standards_profile.json", {"owner": "security"})
    monkeypatch.setattr(security_standards_profile_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_standards_profile_gate, "PROFILE", repo / "governance" / "security" / "security_standards_profile.json"
    )
    monkeypatch.setattr(security_standards_profile_gate, "evidence_root", lambda: ev)
    assert security_standards_profile_gate.main([]) == 1
    report = json.loads((ev / "security" / "security_standards_profile_gate.json").read_text(encoding="utf-8"))
    assert "missing_field:profile_name" in report["findings"]
