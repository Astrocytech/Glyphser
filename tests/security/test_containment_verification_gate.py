from __future__ import annotations

import json
from pathlib import Path

from tooling.security import containment_verification_gate


def test_containment_verification_gate_passes_when_lockdown_disabled(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    pol = repo / "governance" / "security" / "emergency_lockdown_policy.json"
    pol.parent.mkdir(parents=True, exist_ok=True)
    pol.write_text(json.dumps({"lockdown_enabled": False}) + "\n", encoding="utf-8")
    monkeypatch.setattr(containment_verification_gate, "ROOT", repo)
    monkeypatch.setattr(containment_verification_gate, "LOCKDOWN_POLICY", pol)
    monkeypatch.setattr(containment_verification_gate, "evidence_root", lambda: repo / "evidence")
    assert containment_verification_gate.main([]) == 0


def test_containment_verification_gate_fails_without_artifact_when_lockdown_enabled(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    pol = repo / "governance" / "security" / "emergency_lockdown_policy.json"
    pol.parent.mkdir(parents=True, exist_ok=True)
    pol.write_text(json.dumps({"lockdown_enabled": True}) + "\n", encoding="utf-8")
    monkeypatch.setattr(containment_verification_gate, "ROOT", repo)
    monkeypatch.setattr(containment_verification_gate, "LOCKDOWN_POLICY", pol)
    monkeypatch.setattr(containment_verification_gate, "evidence_root", lambda: repo / "evidence")
    assert containment_verification_gate.main([]) == 1
