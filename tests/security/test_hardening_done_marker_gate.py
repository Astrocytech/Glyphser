from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_done_marker_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_done_marker_gate_passes_without_done_marker(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    _write(todo, "A. Alpha\n[ ] pending item\n")
    monkeypatch.setattr(hardening_done_marker_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_done_marker_gate, "DEFAULT_TODO", todo)
    monkeypatch.setattr(hardening_done_marker_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_done_marker_gate.main([]) == 0


def test_hardening_done_marker_gate_fails_when_done_and_pending_exist(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    _write(todo, "A. Alpha\n[ ] pending item\nDONE\n")
    monkeypatch.setattr(hardening_done_marker_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_done_marker_gate, "DEFAULT_TODO", todo)
    monkeypatch.setattr(hardening_done_marker_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_done_marker_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_done_marker_gate.json").read_text(encoding="utf-8"))
    assert "historical_done_marker_ignored_pending_a_ab" in report["findings"]


def test_hardening_done_marker_gate_passes_when_done_and_verification_green(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    _write(todo, "A. Alpha\n[x] done item\nDONE\n")
    _write_json(
        repo / "evidence" / "security" / "hardening_done_marker_verification.json",
        {"ci_status": "green", "verified_completed_items": 1},
    )
    _write_json(repo / "evidence" / "security" / "hardening_terminal_completion_validator.json", {"status": "PASS"})
    _write_json(repo / "evidence" / "security" / "hardening_completed_item_proof_audit.json", {"status": "PASS"})
    _write_json(repo / "evidence" / "security" / "hardening_trigger_backed_findings_validator.json", {"status": "PASS"})
    monkeypatch.setattr(hardening_done_marker_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_done_marker_gate, "DEFAULT_TODO", todo)
    monkeypatch.setattr(hardening_done_marker_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_done_marker_gate.main([]) == 0


def test_hardening_done_marker_gate_fails_when_verification_does_not_cover_all_completed(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    _write(todo, "A. Alpha\n[x] done item one\n[x] done item two\nDONE\n")
    _write_json(
        repo / "evidence" / "security" / "hardening_done_marker_verification.json",
        {"ci_status": "green", "verified_completed_items": 1},
    )
    _write_json(repo / "evidence" / "security" / "hardening_terminal_completion_validator.json", {"status": "PASS"})
    _write_json(repo / "evidence" / "security" / "hardening_completed_item_proof_audit.json", {"status": "PASS"})
    _write_json(repo / "evidence" / "security" / "hardening_trigger_backed_findings_validator.json", {"status": "PASS"})
    monkeypatch.setattr(hardening_done_marker_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_done_marker_gate, "DEFAULT_TODO", todo)
    monkeypatch.setattr(hardening_done_marker_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_done_marker_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_done_marker_gate.json").read_text(encoding="utf-8"))
    assert "done_marker_verification_incomplete_completed_items" in report["findings"]


def test_hardening_done_marker_gate_fails_when_required_validator_not_pass(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    todo = repo / "glyphser_security_hardening_master_todo.txt"
    _write(todo, "A. Alpha\n[x] done item\nDONE\n")
    _write_json(
        repo / "evidence" / "security" / "hardening_done_marker_verification.json",
        {"ci_status": "green", "verified_completed_items": 1},
    )
    _write_json(repo / "evidence" / "security" / "hardening_terminal_completion_validator.json", {"status": "FAIL"})
    _write_json(repo / "evidence" / "security" / "hardening_completed_item_proof_audit.json", {"status": "PASS"})
    _write_json(repo / "evidence" / "security" / "hardening_trigger_backed_findings_validator.json", {"status": "PASS"})
    monkeypatch.setattr(hardening_done_marker_gate, "ROOT", repo)
    monkeypatch.setattr(hardening_done_marker_gate, "DEFAULT_TODO", todo)
    monkeypatch.setattr(hardening_done_marker_gate, "evidence_root", lambda: repo / "evidence")
    assert hardening_done_marker_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_done_marker_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("required_validator_not_pass:hardening_terminal_completion_validator.json:") for item in report["findings"])
