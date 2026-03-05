from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_priority_rubric_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_priority_rubric_gate_passes_for_allowed_priority(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(repo / "governance" / "security" / "hardening_priority_rubric.json", {"allowed_priorities": ["P3 opportunistic"]})
    _write_json(repo / "governance" / "security" / "hardening_pending_item_registry.json", {"entries": [{"id": "SEC-HARD-0001", "priority": "P3 opportunistic"}]})
    monkeypatch.setattr(hardening_priority_rubric_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_priority_rubric_gate, "POLICY", repo / "governance" / "security" / "hardening_priority_rubric.json")
    monkeypatch.setattr(hardening_priority_rubric_gate, "REGISTRY", repo / "governance" / "security" / "hardening_pending_item_registry.json")
    monkeypatch.setattr(hardening_priority_rubric_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_priority_rubric_gate.main([]) == 0


def test_hardening_priority_rubric_gate_fails_for_unknown_priority(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(repo / "governance" / "security" / "hardening_priority_rubric.json", {"allowed_priorities": ["P1 critical"]})
    _write_json(repo / "governance" / "security" / "hardening_pending_item_registry.json", {"entries": [{"id": "SEC-HARD-0001", "priority": "P9"}]})
    monkeypatch.setattr(hardening_priority_rubric_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_priority_rubric_gate, "POLICY", repo / "governance" / "security" / "hardening_priority_rubric.json")
    monkeypatch.setattr(hardening_priority_rubric_gate, "REGISTRY", repo / "governance" / "security" / "hardening_pending_item_registry.json")
    monkeypatch.setattr(hardening_priority_rubric_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_priority_rubric_gate.main([]) == 1
