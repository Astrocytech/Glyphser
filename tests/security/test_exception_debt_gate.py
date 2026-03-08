from __future__ import annotations

import json
from pathlib import Path

from tooling.security import exception_debt_gate


def test_exception_debt_gate_passes_within_budget(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "temporary_exceptions.json").write_text(
        json.dumps(
            {
                "exceptions": [
                    {
                        "id": "e1",
                        "owner": "sec",
                        "reason": "long enough operational exception justification",
                        "expires_at_utc": "2099-01-01T00:00:00+00:00",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(exception_debt_gate, "ROOT", repo)
    monkeypatch.setattr(exception_debt_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        exception_debt_gate,
        "load_policy",
        lambda: {"exception_debt_budget": 5, "minimum_exception_reason_length": 10},
    )
    assert exception_debt_gate.main([]) == 0


def test_exception_debt_gate_fails_on_budget_or_quality(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "temporary_exceptions.json").write_text(
        json.dumps(
            {
                "exceptions": [
                    {"id": "e1", "owner": "", "reason": "short", "expires_at_utc": "2099-01-01T00:00:00+00:00"},
                    {"id": "e2", "owner": "sec", "reason": "short", "expires_at_utc": "2099-01-01T00:00:00+00:00"},
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(exception_debt_gate, "ROOT", repo)
    monkeypatch.setattr(exception_debt_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        exception_debt_gate,
        "load_policy",
        lambda: {"exception_debt_budget": 1, "minimum_exception_reason_length": 24},
    )
    assert exception_debt_gate.main([]) == 1
