from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_dead_gate_wiring_gate


def test_security_dead_gate_wiring_gate_passes_when_gate_referenced(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    wf = repo / ".github" / "workflows"
    ev = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    wf.mkdir(parents=True)
    ev.mkdir(parents=True)
    (sec / "alpha_gate.py").write_text("def main():\n    return 0\n", encoding="utf-8")
    (sec / "security_super_gate.py").write_text("alpha_gate.py\n", encoding="utf-8")
    (wf / "ci.yml").write_text("jobs:\n  test:\n    runs-on: ubuntu-latest\n", encoding="utf-8")

    monkeypatch.setattr(security_dead_gate_wiring_gate, "ROOT", repo)
    monkeypatch.setattr(security_dead_gate_wiring_gate, "evidence_root", lambda: repo / "evidence")
    assert security_dead_gate_wiring_gate.main([]) == 0


def test_security_dead_gate_wiring_gate_fails_when_gate_unreferenced(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    wf = repo / ".github" / "workflows"
    ev = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    wf.mkdir(parents=True)
    ev.mkdir(parents=True)
    (sec / "alpha_gate.py").write_text("def main():\n    return 0\n", encoding="utf-8")
    (sec / "security_super_gate.py").write_text("# no refs\n", encoding="utf-8")
    (wf / "ci.yml").write_text("jobs:\n  test:\n    runs-on: ubuntu-latest\n", encoding="utf-8")

    monkeypatch.setattr(security_dead_gate_wiring_gate, "ROOT", repo)
    monkeypatch.setattr(security_dead_gate_wiring_gate, "evidence_root", lambda: repo / "evidence")
    assert security_dead_gate_wiring_gate.main([]) == 1
    report = json.loads((ev / "security_dead_gate_wiring_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "dead_gate_not_wired:alpha_gate.py" in report["findings"]
