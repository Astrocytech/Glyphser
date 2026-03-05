from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_dependency_graph


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_dependency_graph_reports_order(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {"id": "SEC-HARD-0001", "dependencies": []},
                {"id": "SEC-HARD-0002", "dependencies": ["SEC-HARD-0001"]},
            ]
        },
    )
    monkeypatch.setattr(hardening_dependency_graph, "ROOT", repo)
    monkeypatch.setattr(hardening_dependency_graph, "REGISTRY", registry)
    monkeypatch.setattr(hardening_dependency_graph, "evidence_root", lambda: repo / "evidence")
    assert hardening_dependency_graph.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "hardening_dependency_graph.json").read_text(encoding="utf-8"))
    assert report["order"] == ["SEC-HARD-0001", "SEC-HARD-0002"]


def test_hardening_dependency_graph_fails_on_cycle(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {"id": "SEC-HARD-0001", "dependencies": ["SEC-HARD-0002"]},
                {"id": "SEC-HARD-0002", "dependencies": ["SEC-HARD-0001"]},
            ]
        },
    )
    monkeypatch.setattr(hardening_dependency_graph, "ROOT", repo)
    monkeypatch.setattr(hardening_dependency_graph, "REGISTRY", registry)
    monkeypatch.setattr(hardening_dependency_graph, "evidence_root", lambda: repo / "evidence")
    assert hardening_dependency_graph.main([]) == 1
