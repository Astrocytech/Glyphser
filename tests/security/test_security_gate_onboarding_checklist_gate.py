from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_gate_onboarding_checklist_gate


def test_security_gate_onboarding_checklist_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    chk = repo / "governance" / "security" / "SECURITY_GATE_ONBOARDING_CHECKLIST.md"
    chk.parent.mkdir(parents=True)
    chk.write_text(
        "status\nfindings\nsummary\nmetadata\ntests/security\nsecurity_super_gate.py\nsecurity_super_gate_manifest.json\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_gate_onboarding_checklist_gate, "ROOT", repo)
    monkeypatch.setattr(security_gate_onboarding_checklist_gate, "CHECKLIST", chk)
    monkeypatch.setattr(security_gate_onboarding_checklist_gate, "evidence_root", lambda: repo / "evidence")
    assert security_gate_onboarding_checklist_gate.main([]) == 0


def test_security_gate_onboarding_checklist_gate_fails_when_missing_phrases(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    chk = repo / "governance" / "security" / "SECURITY_GATE_ONBOARDING_CHECKLIST.md"
    chk.parent.mkdir(parents=True)
    chk.write_text("status\nfindings\n", encoding="utf-8")
    monkeypatch.setattr(security_gate_onboarding_checklist_gate, "ROOT", repo)
    monkeypatch.setattr(security_gate_onboarding_checklist_gate, "CHECKLIST", chk)
    monkeypatch.setattr(security_gate_onboarding_checklist_gate, "evidence_root", lambda: repo / "evidence")
    assert security_gate_onboarding_checklist_gate.main([]) == 1
    payload = json.loads(
        (repo / "evidence" / "security" / "security_gate_onboarding_checklist_gate.json").read_text("utf-8")
    )
    assert payload["status"] == "FAIL"
    assert any(str(item).startswith("missing_checklist_phrase:") for item in payload["findings"])
