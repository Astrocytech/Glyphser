from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_completion_metrics


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_completion_metrics_exports_daily_pending_item_count(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    todo.parent.mkdir(parents=True, exist_ok=True)
    todo.write_text("A1. Alpha\n[ ] item 1\n[x] item 2\n[ ] item 3\n", encoding="utf-8")

    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {"id": "SEC-HARD-0001", "status": "done"},
                {"id": "SEC-HARD-0002", "status": "pending"},
            ]
        },
    )

    monkeypatch.setattr(hardening_completion_metrics, "ROOT", repo)
    monkeypatch.setattr(hardening_completion_metrics, "TODO", todo)
    monkeypatch.setattr(hardening_completion_metrics, "REGISTRY", registry)
    monkeypatch.setattr(hardening_completion_metrics, "PERSISTENT_HISTORY", repo / "evidence" / "security" / "hardening_completion_metrics_history.json")
    monkeypatch.setattr(hardening_completion_metrics, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(hardening_completion_metrics, "_today_utc", lambda: "2026-03-05")

    assert hardening_completion_metrics.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "hardening_completion_metrics.json").read_text(encoding="utf-8"))
    assert report["metrics"]["pending_item_count"]["value"] == 2
    assert report["metrics"]["hardening_throughput"]["value"] == 1
    assert report["metrics"]["regression_reopen_rate"]["value"] == 0.0
    history = json.loads((repo / "evidence" / "security" / "hardening_completion_metrics_history.json").read_text(encoding="utf-8"))
    assert history["daily"] == [
        {"date": "2026-03-05", "done_count": 1, "pending_item_count": 2, "regression_reopen_total": 0}
    ]


def test_hardening_completion_metrics_updates_existing_day(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    todo.parent.mkdir(parents=True, exist_ok=True)
    todo.write_text("A1. Alpha\n[ ] item 1\n", encoding="utf-8")

    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(registry, {"entries": [{"id": "SEC-HARD-0001", "status": "done"}]})

    history_path = repo / "evidence" / "security" / "hardening_completion_metrics_history.json"
    _write_json(
        history_path,
        {
            "schema_version": 1,
            "updated_at_utc": "2026-03-04T00:00:00+00:00",
            "daily": [{"date": "2026-03-05", "pending_item_count": 99, "done_count": 5, "regression_reopen_total": 2}],
        },
    )

    monkeypatch.setattr(hardening_completion_metrics, "ROOT", repo)
    monkeypatch.setattr(hardening_completion_metrics, "TODO", todo)
    monkeypatch.setattr(hardening_completion_metrics, "REGISTRY", registry)
    monkeypatch.setattr(hardening_completion_metrics, "PERSISTENT_HISTORY", history_path)
    monkeypatch.setattr(hardening_completion_metrics, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(hardening_completion_metrics, "_today_utc", lambda: "2026-03-05")

    assert hardening_completion_metrics.main([]) == 0
    history = json.loads(history_path.read_text(encoding="utf-8"))
    assert history["daily"] == [
        {"date": "2026-03-05", "done_count": 1, "pending_item_count": 1, "regression_reopen_total": 0}
    ]


def test_hardening_completion_metrics_computes_weekly_throughput_from_history(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    todo.parent.mkdir(parents=True, exist_ok=True)
    todo.write_text("A1. Alpha\\n[ ] item 1\\n", encoding="utf-8")
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {"id": "SEC-HARD-0001", "status": "done"},
                {"id": "SEC-HARD-0002", "status": "done"},
                {"id": "SEC-HARD-0003", "status": "done"},
            ]
        },
    )
    history_path = repo / "evidence" / "security" / "hardening_completion_metrics_history.json"
    _write_json(
        history_path,
        {
            "schema_version": 1,
            "updated_at_utc": "2026-03-11T00:00:00+00:00",
            "daily": [
                {"date": "2026-03-05", "pending_item_count": 9, "done_count": 1, "regression_reopen_total": 0},
                {"date": "2026-03-06", "pending_item_count": 8, "done_count": 2, "regression_reopen_total": 0},
            ],
        },
    )

    monkeypatch.setattr(hardening_completion_metrics, "ROOT", repo)
    monkeypatch.setattr(hardening_completion_metrics, "TODO", todo)
    monkeypatch.setattr(hardening_completion_metrics, "REGISTRY", registry)
    monkeypatch.setattr(hardening_completion_metrics, "PERSISTENT_HISTORY", history_path)
    monkeypatch.setattr(hardening_completion_metrics, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(hardening_completion_metrics, "_today_utc", lambda: "2026-03-12")

    assert hardening_completion_metrics.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "hardening_completion_metrics.json").read_text(encoding="utf-8"))
    assert report["metrics"]["hardening_throughput"]["value"] == 2


def test_hardening_completion_metrics_computes_regression_reopen_rate(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    todo.parent.mkdir(parents=True, exist_ok=True)
    todo.write_text("A1. Alpha\\n[ ] item 1\\n", encoding="utf-8")
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(
        registry,
        {
            "entries": [
                {"id": "SEC-HARD-0001", "status": "done"},
                {"id": "SEC-HARD-0002", "status": "done"},
                {"id": "SEC-HARD-0003", "status": "done"},
                {"id": "SEC-HARD-0004", "status": "in_progress", "reopen_reason": "regression_detected"},
                {"id": "SEC-HARD-0005", "status": "in_progress", "reopen_reason": "regression_detected"},
            ]
        },
    )
    history_path = repo / "evidence" / "security" / "hardening_completion_metrics_history.json"
    _write_json(
        history_path,
        {
            "schema_version": 1,
            "updated_at_utc": "2026-03-11T00:00:00+00:00",
            "daily": [
                {"date": "2026-03-05", "pending_item_count": 9, "done_count": 1, "regression_reopen_total": 1},
            ],
        },
    )

    monkeypatch.setattr(hardening_completion_metrics, "ROOT", repo)
    monkeypatch.setattr(hardening_completion_metrics, "TODO", todo)
    monkeypatch.setattr(hardening_completion_metrics, "REGISTRY", registry)
    monkeypatch.setattr(hardening_completion_metrics, "PERSISTENT_HISTORY", history_path)
    monkeypatch.setattr(hardening_completion_metrics, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(hardening_completion_metrics, "_today_utc", lambda: "2026-03-12")

    assert hardening_completion_metrics.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "hardening_completion_metrics.json").read_text(encoding="utf-8"))
    assert report["metrics"]["hardening_throughput"]["value"] == 2
    assert report["metrics"]["regression_reopen_rate"]["value"] == 0.5


def test_hardening_completion_metrics_tracks_ci_security_green_streak(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    todo.parent.mkdir(parents=True, exist_ok=True)
    todo.write_text("A1. Alpha\\n[ ] item 1\\n", encoding="utf-8")
    registry = repo / "governance" / "security" / "hardening_pending_item_registry.json"
    _write_json(registry, {"entries": []})
    history_path = repo / "evidence" / "security" / "hardening_completion_metrics_history.json"
    _write_json(
        history_path,
        {
            "schema_version": 1,
            "updated_at_utc": "2026-03-11T00:00:00+00:00",
            "daily": [],
            "runs": [{"date": "2026-03-11", "ci_security_green": True, "timestamp_utc": "2026-03-11T00:00:00+00:00"}],
        },
    )

    sec = repo / "evidence" / "security"
    _write_json(sec / "example_gate.json", {"status": "PASS", "findings": []})

    monkeypatch.setattr(hardening_completion_metrics, "ROOT", repo)
    monkeypatch.setattr(hardening_completion_metrics, "TODO", todo)
    monkeypatch.setattr(hardening_completion_metrics, "REGISTRY", registry)
    monkeypatch.setattr(hardening_completion_metrics, "PERSISTENT_HISTORY", history_path)
    monkeypatch.setattr(hardening_completion_metrics, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(hardening_completion_metrics, "_today_utc", lambda: "2026-03-12")

    assert hardening_completion_metrics.main([]) == 0
    report = json.loads((sec / "hardening_completion_metrics.json").read_text(encoding="utf-8"))
    assert report["metrics"]["ci_security_green_streak"]["value"] == 2
