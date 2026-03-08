from __future__ import annotations

import json
from pathlib import Path

from tooling.security import helper_script_enforcement_gate


def test_helper_script_enforcement_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    (sec / "ok.py").write_text("raise SystemExit(1)\n", encoding="utf-8")
    monkeypatch.setattr(helper_script_enforcement_gate, "ROOT", repo)
    monkeypatch.setattr(helper_script_enforcement_gate, "SECURITY_DIR", sec)
    monkeypatch.setattr(helper_script_enforcement_gate, "evidence_root", lambda: repo / "evidence")
    assert helper_script_enforcement_gate.main([]) == 0


def test_helper_script_enforcement_gate_fails_on_forced_success(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    (sec / "bad.py").write_text("raise SystemExit(0)\n", encoding="utf-8")
    monkeypatch.setattr(helper_script_enforcement_gate, "ROOT", repo)
    monkeypatch.setattr(helper_script_enforcement_gate, "SECURITY_DIR", sec)
    monkeypatch.setattr(helper_script_enforcement_gate, "evidence_root", lambda: repo / "evidence")
    assert helper_script_enforcement_gate.main([]) == 1
    payload = json.loads((repo / "evidence" / "security" / "helper_script_enforcement_gate.json").read_text())
    assert any(str(item).startswith("forced_success_exit:") for item in payload["findings"])
