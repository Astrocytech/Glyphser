from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_status_exitcode_consistency_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_security_status_exitcode_consistency_gate_passes_with_mapping(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(sec / "alpha_gate.py", 'def main():\n    return 0 if report["status"] == "PASS" else 1\n')

    monkeypatch.setattr(security_status_exitcode_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(security_status_exitcode_consistency_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_status_exitcode_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_status_exitcode_consistency_gate.main([]) == 0


def test_security_status_exitcode_consistency_gate_fails_without_mapping(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    _write(sec / "beta_gate.py", "def main():\n    return 0\n")

    monkeypatch.setattr(security_status_exitcode_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(security_status_exitcode_consistency_gate, "SECURITY_TOOLING", sec)
    monkeypatch.setattr(security_status_exitcode_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_status_exitcode_consistency_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_status_exitcode_consistency_gate.json").read_text(encoding="utf-8"))
    assert "missing_status_exitcode_mapping:beta_gate.py" in report["findings"]
