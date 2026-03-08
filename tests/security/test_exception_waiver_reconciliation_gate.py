from __future__ import annotations

import json
from pathlib import Path

from tooling.security import exception_waiver_reconciliation_gate


def _seed_waiver_policy(repo: Path) -> None:
    pol = repo / "governance" / "security" / "temporary_waiver_policy.json"
    pol.parent.mkdir(parents=True, exist_ok=True)
    pol.write_text(json.dumps({"waiver_file_glob": "evidence/**/waivers.json"}) + "\n", encoding="utf-8")


def test_exception_waiver_reconciliation_gate_passes_without_expired_waivers(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_waiver_policy(repo)
    (repo / "governance" / "security" / "temporary_exceptions.json").write_text(
        json.dumps({"exceptions": [], "closed_waivers": []}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(exception_waiver_reconciliation_gate, "ROOT", repo)
    monkeypatch.setattr(
        exception_waiver_reconciliation_gate,
        "WAIVER_POLICY",
        repo / "governance/security/temporary_waiver_policy.json",
    )
    monkeypatch.setattr(
        exception_waiver_reconciliation_gate,
        "EXCEPTIONS_FILE",
        repo / "governance/security/temporary_exceptions.json",
    )
    monkeypatch.setattr(exception_waiver_reconciliation_gate, "evidence_root", lambda: repo / "evidence")
    assert exception_waiver_reconciliation_gate.main([]) == 0


def test_exception_waiver_reconciliation_gate_fails_when_expired_waiver_not_closed(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _seed_waiver_policy(repo)
    (repo / "governance" / "security" / "temporary_exceptions.json").write_text(
        json.dumps({"exceptions": [], "closed_waivers": []}) + "\n",
        encoding="utf-8",
    )
    waivers = repo / "evidence" / "repro" / "waivers.json"
    waivers.parent.mkdir(parents=True, exist_ok=True)
    waivers.write_text(
        json.dumps({"waivers": [{"id": "w1", "expires_at_utc": "2000-01-01T00:00:00+00:00"}]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(exception_waiver_reconciliation_gate, "ROOT", repo)
    monkeypatch.setattr(
        exception_waiver_reconciliation_gate,
        "WAIVER_POLICY",
        repo / "governance/security/temporary_waiver_policy.json",
    )
    monkeypatch.setattr(
        exception_waiver_reconciliation_gate,
        "EXCEPTIONS_FILE",
        repo / "governance/security/temporary_exceptions.json",
    )
    monkeypatch.setattr(exception_waiver_reconciliation_gate, "evidence_root", lambda: repo / "evidence")
    assert exception_waiver_reconciliation_gate.main([]) == 1
