from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_actionable_findings_gate


def test_security_actionable_findings_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "a.json").write_text('{"status":"PASS","findings":[]}\n', encoding="utf-8")
    (sec / "b.json").write_text('{"status":"FAIL","findings":["code_one:detail","code_two:item"]}\n', encoding="utf-8")
    monkeypatch.setattr(security_actionable_findings_gate, "evidence_root", lambda: repo / "evidence")
    assert security_actionable_findings_gate.main([]) == 0


def test_security_actionable_findings_gate_fails_on_missing_codes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "b.json").write_text('{"status":"FAIL","findings":["bad finding"]}\n', encoding="utf-8")
    monkeypatch.setattr(security_actionable_findings_gate, "evidence_root", lambda: repo / "evidence")
    assert security_actionable_findings_gate.main([]) == 1
    payload = json.loads((sec / "security_actionable_findings_gate.json").read_text(encoding="utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("non_actionable_finding:") for item in payload["findings"])
