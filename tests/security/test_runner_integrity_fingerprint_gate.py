from __future__ import annotations

import json
from types import SimpleNamespace
from pathlib import Path

from tooling.security import runner_integrity_fingerprint_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_runner_integrity_fingerprint_gate_passes_when_allowlisted(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    gov = repo / "governance" / "security"
    (repo / "evidence" / "security").mkdir(parents=True)
    _write(
        gov / "runner_integrity_fingerprint_policy.json",
        {
            "allowed_fingerprints": [{"runner_os": "linux", "python_minor": "3.12"}],
            "require_match_in_envs": ["ci"],
        },
    )
    monkeypatch.setattr(runner_integrity_fingerprint_gate, "ROOT", repo)
    monkeypatch.setattr(
        runner_integrity_fingerprint_gate,
        "POLICY",
        gov / "runner_integrity_fingerprint_policy.json",
    )
    monkeypatch.setattr(runner_integrity_fingerprint_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_ENV", "ci")
    monkeypatch.setenv("RUNNER_OS", "Linux")
    monkeypatch.setattr(runner_integrity_fingerprint_gate.sys, "version_info", SimpleNamespace(major=3, minor=12))
    assert runner_integrity_fingerprint_gate.main([]) == 0


def test_runner_integrity_fingerprint_gate_fails_when_unallowlisted_in_ci(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    gov = repo / "governance" / "security"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write(
        gov / "runner_integrity_fingerprint_policy.json",
        {
            "allowed_fingerprints": [{"runner_os": "linux", "python_minor": "3.11"}],
            "require_match_in_envs": ["ci"],
        },
    )
    monkeypatch.setattr(runner_integrity_fingerprint_gate, "ROOT", repo)
    monkeypatch.setattr(
        runner_integrity_fingerprint_gate,
        "POLICY",
        gov / "runner_integrity_fingerprint_policy.json",
    )
    monkeypatch.setattr(runner_integrity_fingerprint_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_ENV", "ci")
    monkeypatch.setenv("RUNNER_OS", "Linux")
    monkeypatch.setattr(runner_integrity_fingerprint_gate.sys, "version_info", SimpleNamespace(major=3, minor=12))
    assert runner_integrity_fingerprint_gate.main([]) == 1
    payload = json.loads((sec / "runner_integrity_fingerprint_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("runner_fingerprint_not_allowlisted:") for item in payload["findings"])
