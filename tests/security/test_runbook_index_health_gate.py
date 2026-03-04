from __future__ import annotations

import json
from pathlib import Path

from tooling.security import runbook_index_health_gate


def test_runbook_index_health_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "governance" / "security"
    sec.mkdir(parents=True)
    (sec / "PLAYBOOK.md").write_text("# Playbook\n", encoding="utf-8")
    (sec / "INDEX.md").write_text("[Playbook](PLAYBOOK.md)\n", encoding="utf-8")
    monkeypatch.setattr(runbook_index_health_gate, "ROOT", repo)
    monkeypatch.setattr(runbook_index_health_gate, "DOC_ROOTS", [sec])
    monkeypatch.setattr(runbook_index_health_gate, "evidence_root", lambda: repo / "evidence")
    assert runbook_index_health_gate.main([]) == 0


def test_runbook_index_health_gate_fails_on_broken_link(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "governance" / "security"
    sec.mkdir(parents=True)
    (sec / "INDEX.md").write_text("[Missing](MISSING.md)\n", encoding="utf-8")
    monkeypatch.setattr(runbook_index_health_gate, "ROOT", repo)
    monkeypatch.setattr(runbook_index_health_gate, "DOC_ROOTS", [sec])
    monkeypatch.setattr(runbook_index_health_gate, "evidence_root", lambda: repo / "evidence")
    assert runbook_index_health_gate.main([]) == 1
    payload = json.loads((repo / "evidence" / "security" / "runbook_index_health_gate.json").read_text("utf-8"))
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("broken_link:") for item in payload["findings"])
