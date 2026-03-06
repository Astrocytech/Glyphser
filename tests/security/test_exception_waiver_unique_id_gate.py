from __future__ import annotations

import json
from pathlib import Path

from tooling.security import exception_waiver_unique_id_gate


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _write_control_matrix(repo: Path, control_ids: list[str]) -> Path:
    path = repo / "governance" / "security" / "threat_control_matrix.json"
    _write_json(path, {"controls": [{"id": control_id} for control_id in control_ids]})
    return path


def test_exception_waiver_unique_id_gate_passes_for_unique_ids(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    matrix = _write_control_matrix(repo, ["CTRL-1", "CTRL-2"])
    _write_json(
        repo / "governance" / "security" / "temporary_exceptions.json",
        {"exceptions": [{"id": "EX-1"}, {"id": "EX-2"}]},
    )
    _write_json(
        repo / "evidence" / "repro" / "waivers.json",
        {"waivers": [{"id": "W-1"}, {"id": "W-2"}]},
    )
    monkeypatch.setattr(exception_waiver_unique_id_gate, "ROOT", repo)
    monkeypatch.setattr(
        exception_waiver_unique_id_gate, "EXCEPTIONS_PATH", repo / "governance" / "security" / "temporary_exceptions.json"
    )
    monkeypatch.setattr(exception_waiver_unique_id_gate, "CONTROL_MATRIX_PATH", matrix)
    monkeypatch.setattr(exception_waiver_unique_id_gate, "evidence_root", lambda: repo / "evidence")
    assert exception_waiver_unique_id_gate.main([]) == 0


def test_exception_waiver_unique_id_gate_fails_for_duplicate_id(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    matrix = _write_control_matrix(repo, ["CTRL-1"])
    _write_json(
        repo / "governance" / "security" / "temporary_exceptions.json",
        {"exceptions": [{"id": "EX-1"}]},
    )
    _write_json(
        repo / "evidence" / "repro" / "waivers.json",
        {"waivers": [{"id": "ex-1"}]},
    )
    monkeypatch.setattr(exception_waiver_unique_id_gate, "ROOT", repo)
    monkeypatch.setattr(
        exception_waiver_unique_id_gate, "EXCEPTIONS_PATH", repo / "governance" / "security" / "temporary_exceptions.json"
    )
    monkeypatch.setattr(exception_waiver_unique_id_gate, "CONTROL_MATRIX_PATH", matrix)
    monkeypatch.setattr(exception_waiver_unique_id_gate, "evidence_root", lambda: repo / "evidence")
    assert exception_waiver_unique_id_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "exception_waiver_unique_id_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("duplicate_exception_waiver_id:") for item in report["findings"])


def test_exception_waiver_unique_id_gate_passes_when_exception_controls_exist(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    matrix = _write_control_matrix(repo, ["CTRL-1", "CTRL-2", "CTRL-3"])
    _write_json(
        repo / "governance" / "security" / "temporary_exceptions.json",
        {"exceptions": [{"id": "EX-1", "control_id": "CTRL-1"}, {"id": "EX-2", "control_ids": ["CTRL-2", "CTRL-3"]}]},
    )
    _write_json(repo / "evidence" / "repro" / "waivers.json", {"waivers": [{"id": "W-1"}]})
    monkeypatch.setattr(exception_waiver_unique_id_gate, "ROOT", repo)
    monkeypatch.setattr(
        exception_waiver_unique_id_gate, "EXCEPTIONS_PATH", repo / "governance" / "security" / "temporary_exceptions.json"
    )
    monkeypatch.setattr(exception_waiver_unique_id_gate, "CONTROL_MATRIX_PATH", matrix)
    monkeypatch.setattr(exception_waiver_unique_id_gate, "evidence_root", lambda: repo / "evidence")
    assert exception_waiver_unique_id_gate.main([]) == 0


def test_exception_waiver_unique_id_gate_fails_when_exception_references_deleted_control(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    matrix = _write_control_matrix(repo, ["CTRL-1"])
    _write_json(
        repo / "governance" / "security" / "temporary_exceptions.json",
        {"exceptions": [{"id": "EX-1", "control_id": "CTRL-MISSING"}, {"id": "EX-2", "control_ids": ["CTRL-1", "CTRL-OLD"]}]},
    )
    _write_json(repo / "evidence" / "repro" / "waivers.json", {"waivers": [{"id": "W-1"}]})
    monkeypatch.setattr(exception_waiver_unique_id_gate, "ROOT", repo)
    monkeypatch.setattr(
        exception_waiver_unique_id_gate, "EXCEPTIONS_PATH", repo / "governance" / "security" / "temporary_exceptions.json"
    )
    monkeypatch.setattr(exception_waiver_unique_id_gate, "CONTROL_MATRIX_PATH", matrix)
    monkeypatch.setattr(exception_waiver_unique_id_gate, "evidence_root", lambda: repo / "evidence")
    assert exception_waiver_unique_id_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "exception_waiver_unique_id_gate.json").read_text(encoding="utf-8"))
    assert "exception_references_deleted_control:0:CTRL-MISSING" in report["findings"]
    assert "exception_references_deleted_control:1:CTRL-OLD" in report["findings"]
