from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_wip_limits_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_wip_limits_gate_passes_within_limit(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "hardening_wip_limits_policy.json",
        {"wip_limits": {"wave_1": 2}, "wave_section_prefixes": {"wave_1": ["AB1"]}},
    )
    _write_json(
        repo / "governance" / "security" / "hardening_pending_item_registry.json",
        {"entries": [{"section": "AB1", "status": "in_progress"}]},
    )
    monkeypatch.setattr(hardening_wip_limits_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_wip_limits_gate, "POLICY", repo / "governance" / "security" / "hardening_wip_limits_policy.json")
    monkeypatch.setattr(hardening_wip_limits_gate, "REGISTRY", repo / "governance" / "security" / "hardening_pending_item_registry.json")
    monkeypatch.setattr(hardening_wip_limits_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_wip_limits_gate.main([]) == 0


def test_hardening_wip_limits_gate_fails_when_limit_exceeded(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(
        repo / "governance" / "security" / "hardening_wip_limits_policy.json",
        {"wip_limits": {"wave_1": 1}, "wave_section_prefixes": {"wave_1": ["AB1"]}},
    )
    _write_json(
        repo / "governance" / "security" / "hardening_pending_item_registry.json",
        {"entries": [{"section": "AB1", "status": "in_progress"}, {"section": "AB1", "status": "in_progress"}]},
    )
    monkeypatch.setattr(hardening_wip_limits_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_wip_limits_gate, "POLICY", repo / "governance" / "security" / "hardening_wip_limits_policy.json")
    monkeypatch.setattr(hardening_wip_limits_gate, "REGISTRY", repo / "governance" / "security" / "hardening_pending_item_registry.json")
    monkeypatch.setattr(hardening_wip_limits_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_wip_limits_gate.main([]) == 1
