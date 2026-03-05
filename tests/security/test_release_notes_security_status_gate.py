from __future__ import annotations

import json
from pathlib import Path

from tooling.security import release_notes_security_status_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_release_notes_security_status_gate_passes_with_summary_and_decision(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(repo / "evidence" / "security" / "promotion_go_no_go_report.json", {"summary": {"decision": "GO"}})
    _write(
        repo / "CHANGELOG.md",
        "# Release\n\n## Security Control Status Summary\nDecision: GO\n",
    )

    monkeypatch.setattr(release_notes_security_status_gate, "ROOT", repo)
    monkeypatch.setattr(release_notes_security_status_gate, "PROMOTION_REPORT", repo / "evidence/security/promotion_go_no_go_report.json")
    monkeypatch.setattr(release_notes_security_status_gate, "evidence_root", lambda: repo / "evidence")

    assert release_notes_security_status_gate.main([]) == 0


def test_release_notes_security_status_gate_fails_without_summary(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_json(repo / "evidence" / "security" / "promotion_go_no_go_report.json", {"summary": {"decision": "NO_GO"}})
    _write(repo / "CHANGELOG.md", "# Release\n")

    monkeypatch.setattr(release_notes_security_status_gate, "ROOT", repo)
    monkeypatch.setattr(release_notes_security_status_gate, "PROMOTION_REPORT", repo / "evidence/security/promotion_go_no_go_report.json")
    monkeypatch.setattr(release_notes_security_status_gate, "evidence_root", lambda: repo / "evidence")

    assert release_notes_security_status_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "release_notes_security_status_gate.json").read_text(encoding="utf-8"))
    assert "missing_security_control_status_summary_section" in report["findings"]
