from __future__ import annotations

import json
from pathlib import Path

from tooling.security import ruff_security_profile_gate


def test_ruff_security_profile_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profile = repo / "tooling" / "security" / "ruff_security_profile.toml"
    profile.parent.mkdir(parents=True)
    profile.write_text(
        'line-length = 120\n'
        '[lint]\n'
        'select = ["E", "F", "I", "C90"]\n'
        '[lint.mccabe]\n'
        "max-complexity = 12\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ruff_security_profile_gate, "ROOT", repo)
    monkeypatch.setattr(ruff_security_profile_gate, "PROFILE", profile)
    monkeypatch.setattr(ruff_security_profile_gate, "evidence_root", lambda: repo / "evidence")
    assert ruff_security_profile_gate.main([]) == 0


def test_ruff_security_profile_gate_fails_on_missing_rule(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    profile = repo / "tooling" / "security" / "ruff_security_profile.toml"
    profile.parent.mkdir(parents=True)
    profile.write_text(
        '[lint]\n'
        'select = ["E", "F"]\n'
        '[lint.mccabe]\n'
        "max-complexity = 25\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(ruff_security_profile_gate, "ROOT", repo)
    monkeypatch.setattr(ruff_security_profile_gate, "PROFILE", profile)
    monkeypatch.setattr(ruff_security_profile_gate, "evidence_root", lambda: repo / "evidence")
    assert ruff_security_profile_gate.main([]) == 1
    payload = json.loads((repo / "evidence" / "security" / "ruff_security_profile_gate.json").read_text("utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("missing_rule_select:") for item in payload["findings"])
    assert any(str(item).startswith("mccabe_max_too_high:") for item in payload["findings"])
