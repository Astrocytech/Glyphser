from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_terminal_completion_validator


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_terminal_completion_validator_passes_when_all_conditions_met(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    _write(todo, "A. Alpha\n[x] done\nDONE\n")
    exceptions = repo / "governance" / "security" / "temporary_exceptions.json"
    _write_json(exceptions, {"exceptions": []})
    policy = repo / "governance" / "security" / "hardening_terminal_completion_policy.json"
    _write_json(policy, {"last_n_security_runs_green": 2})
    history = repo / "evidence" / "security" / "hardening_completion_metrics_history.json"
    _write_json(
        history,
        {
            "runs": [
                {"ci_security_green": True},
                {"ci_security_green": True},
            ]
        },
    )

    monkeypatch.setattr(hardening_terminal_completion_validator, "ROOT", repo)
    monkeypatch.setattr(hardening_terminal_completion_validator, "TODO", todo)
    monkeypatch.setattr(hardening_terminal_completion_validator, "EXCEPTIONS", exceptions)
    monkeypatch.setattr(hardening_terminal_completion_validator, "POLICY", policy)
    monkeypatch.setattr(hardening_terminal_completion_validator, "METRICS_HISTORY", history)
    monkeypatch.setattr(hardening_terminal_completion_validator, "evidence_root", lambda: repo / "evidence")

    assert hardening_terminal_completion_validator.main([]) == 0


def test_hardening_terminal_completion_validator_fails_on_pending_critical_and_non_green(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    _write(todo, "A. Alpha\n[ ] pending\nDONE\n")
    exceptions = repo / "governance" / "security" / "temporary_exceptions.json"
    _write_json(exceptions, {"exceptions": [{"id": "EX-1", "severity": "critical", "status": "active", "active": True}]})
    policy = repo / "governance" / "security" / "hardening_terminal_completion_policy.json"
    _write_json(policy, {"last_n_security_runs_green": 3})
    history = repo / "evidence" / "security" / "hardening_completion_metrics_history.json"
    _write_json(
        history,
        {
            "runs": [
                {"ci_security_green": True},
                {"ci_security_green": False},
            ]
        },
    )

    monkeypatch.setattr(hardening_terminal_completion_validator, "ROOT", repo)
    monkeypatch.setattr(hardening_terminal_completion_validator, "TODO", todo)
    monkeypatch.setattr(hardening_terminal_completion_validator, "EXCEPTIONS", exceptions)
    monkeypatch.setattr(hardening_terminal_completion_validator, "POLICY", policy)
    monkeypatch.setattr(hardening_terminal_completion_validator, "METRICS_HISTORY", history)
    monkeypatch.setattr(hardening_terminal_completion_validator, "evidence_root", lambda: repo / "evidence")

    assert hardening_terminal_completion_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_terminal_completion_validator.json").read_text(encoding="utf-8"))
    assert any(item.startswith("pending_items_not_zero:") for item in report["findings"])
    assert any(item.startswith("active_critical_exceptions:") for item in report["findings"])
    assert any(item.startswith("last_n_security_runs_not_green:") for item in report["findings"])
