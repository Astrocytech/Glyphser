from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_gate_test_coverage_gate


def test_security_gate_test_coverage_gate_passes_when_gate_has_test(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    tst = repo / "tests" / "security"
    ev = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    tst.mkdir(parents=True)
    ev.mkdir(parents=True)
    (sec / "alpha_gate.py").write_text("def main():\n    return 0\n", encoding="utf-8")
    (tst / "test_alpha_gate.py").write_text("def test_alpha():\n    assert True\n", encoding="utf-8")

    monkeypatch.setattr(security_gate_test_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(security_gate_test_coverage_gate, "evidence_root", lambda: repo / "evidence")
    assert security_gate_test_coverage_gate.main([]) == 0


def test_security_gate_test_coverage_gate_fails_when_gate_has_no_test(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    tst = repo / "tests" / "security"
    ev = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    tst.mkdir(parents=True)
    ev.mkdir(parents=True)
    (sec / "alpha_gate.py").write_text("def main():\n    return 0\n", encoding="utf-8")

    monkeypatch.setattr(security_gate_test_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(security_gate_test_coverage_gate, "evidence_root", lambda: repo / "evidence")
    assert security_gate_test_coverage_gate.main([]) == 1
    report = json.loads((ev / "security_gate_test_coverage.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_test_coverage:alpha_gate" in report["findings"]
