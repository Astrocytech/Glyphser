from __future__ import annotations

import json
from pathlib import Path

from tooling.security import mypy_security_profile_gate


def test_mypy_security_profile_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "mypy.ini").write_text(
        "[mypy-tooling.security.*]\n"
        "disallow_untyped_defs = True\n"
        "disallow_incomplete_defs = True\n"
        "warn_return_any = True\n"
        "[mypy-runtime.glyphser.security.*]\n"
        "disallow_untyped_defs = True\n"
        "disallow_incomplete_defs = True\n"
        "warn_return_any = True\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mypy_security_profile_gate, "ROOT", repo)
    monkeypatch.setattr(mypy_security_profile_gate, "evidence_root", lambda: repo / "evidence")
    assert mypy_security_profile_gate.main([]) == 0


def test_mypy_security_profile_gate_fails_on_missing_setting(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "mypy.ini").write_text(
        "[mypy-tooling.security.*]\n"
        "disallow_untyped_defs = True\n"
        "[mypy-runtime.glyphser.security.*]\n"
        "disallow_untyped_defs = True\n"
        "disallow_incomplete_defs = True\n"
        "warn_return_any = True\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(mypy_security_profile_gate, "ROOT", repo)
    monkeypatch.setattr(mypy_security_profile_gate, "evidence_root", lambda: repo / "evidence")
    assert mypy_security_profile_gate.main([]) == 1
    payload = json.loads((repo / "evidence" / "security" / "mypy_security_profile_gate.json").read_text("utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("invalid_setting:") for item in payload["findings"])
