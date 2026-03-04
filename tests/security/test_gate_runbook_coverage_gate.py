from __future__ import annotations

import json
from pathlib import Path

from tooling.security import gate_runbook_coverage_gate


def test_gate_runbook_coverage_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["tooling/security/a_gate.py"], "extended": ["tooling/security/b_gate.py"]}) + "\n",
        encoding="utf-8",
    )
    (gov / "GATE_RUNBOOK_INDEX.md").write_text("## `a_gate.py`\n\n## `b_gate.py`\n", encoding="utf-8")
    monkeypatch.setattr(gate_runbook_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(gate_runbook_coverage_gate, "MANIFEST", sec / "security_super_gate_manifest.json")
    monkeypatch.setattr(gate_runbook_coverage_gate, "RUNBOOK", gov / "GATE_RUNBOOK_INDEX.md")
    monkeypatch.setattr(gate_runbook_coverage_gate, "evidence_root", lambda: repo / "evidence")
    assert gate_runbook_coverage_gate.main([]) == 0


def test_gate_runbook_coverage_gate_fails_when_sections_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "tooling" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True)
    gov.mkdir(parents=True)
    (sec / "security_super_gate_manifest.json").write_text(
        json.dumps({"core": ["tooling/security/a_gate.py"], "extended": ["tooling/security/b_gate.py"]}) + "\n",
        encoding="utf-8",
    )
    (gov / "GATE_RUNBOOK_INDEX.md").write_text("## `a_gate.py`\n", encoding="utf-8")
    monkeypatch.setattr(gate_runbook_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(gate_runbook_coverage_gate, "MANIFEST", sec / "security_super_gate_manifest.json")
    monkeypatch.setattr(gate_runbook_coverage_gate, "RUNBOOK", gov / "GATE_RUNBOOK_INDEX.md")
    monkeypatch.setattr(gate_runbook_coverage_gate, "evidence_root", lambda: repo / "evidence")
    assert gate_runbook_coverage_gate.main([]) == 1
