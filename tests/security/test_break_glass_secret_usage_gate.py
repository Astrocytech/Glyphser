from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import break_glass_secret_usage_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    sig = sign_file(path, key=current_key(strict=False))
    path.with_suffix(path.suffix + ".sig").write_text(sig + "\n", encoding="utf-8")


def test_break_glass_secret_usage_gate_passes_when_not_used(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(break_glass_secret_usage_gate, "ROOT", repo)
    monkeypatch.setattr(break_glass_secret_usage_gate, "evidence_root", lambda: repo / "evidence")
    assert break_glass_secret_usage_gate.main([]) == 0


def test_break_glass_secret_usage_gate_fails_without_ticket_and_signed_report(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(repo / "evidence" / "security" / "break_glass_secret_usage.json", {"break_glass_secret_used": True})

    monkeypatch.setattr(break_glass_secret_usage_gate, "ROOT", repo)
    monkeypatch.setattr(break_glass_secret_usage_gate, "evidence_root", lambda: repo / "evidence")
    assert break_glass_secret_usage_gate.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "break_glass_secret_usage_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_incident_ticket" in report["findings"]


def test_break_glass_secret_usage_gate_passes_with_ticket_and_signed_report(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    report_path = repo / "evidence" / "security" / "after_action_report.json"
    _write_json(report_path, {"status": "closed"})
    _sign(report_path)
    _write_json(
        repo / "evidence" / "security" / "break_glass_secret_usage.json",
        {
            "break_glass_secret_used": True,
            "incident_ticket": "INC-123",
            "after_action_report": "evidence/security/after_action_report.json",
        },
    )

    monkeypatch.setattr(break_glass_secret_usage_gate, "ROOT", repo)
    monkeypatch.setattr(break_glass_secret_usage_gate, "evidence_root", lambda: repo / "evidence")
    assert break_glass_secret_usage_gate.main([]) == 0
