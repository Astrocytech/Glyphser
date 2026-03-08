from __future__ import annotations

import json
from pathlib import Path

from tooling.security import exception_path_metadata_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_exception_path_metadata_gate_passes_with_required_fields(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(
        repo / "governance" / "security" / "temporary_exceptions.json",
        {
            "exceptions": [
                {
                    "id": "EX-1",
                    "owner": "security-team",
                    "reason": "temporary exception for release lane rollback drill",
                    "expires_at_utc": "2099-01-01T00:00:00+00:00",
                }
            ]
        },
    )
    _write_json(
        repo / "evidence" / "repro" / "waivers.json",
        {
            "waivers": [
                {
                    "id": "W-1",
                    "owner": "security-team",
                    "justification": "documented non-blocking fallback for staged migration",
                    "expires_at_utc": "2099-01-01T00:00:00+00:00",
                }
            ]
        },
    )

    monkeypatch.setattr(exception_path_metadata_gate, "ROOT", repo)
    monkeypatch.setattr(
        exception_path_metadata_gate,
        "EXCEPTIONS_FILE",
        repo / "governance" / "security" / "temporary_exceptions.json",
    )
    monkeypatch.setattr(exception_path_metadata_gate, "WAIVERS_FILE", repo / "evidence" / "repro" / "waivers.json")
    monkeypatch.setattr(exception_path_metadata_gate, "evidence_root", lambda: ev)

    assert exception_path_metadata_gate.main([]) == 0
    report = json.loads((ev / "security" / "exception_path_metadata_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"


def test_exception_path_metadata_gate_fails_on_missing_fields(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"

    _write_json(repo / "governance" / "security" / "temporary_exceptions.json", {"exceptions": [{"id": "EX-1"}]})
    _write_json(repo / "evidence" / "repro" / "waivers.json", {"waivers": [{"id": "W-1", "owner": "sec"}]})

    monkeypatch.setattr(exception_path_metadata_gate, "ROOT", repo)
    monkeypatch.setattr(
        exception_path_metadata_gate,
        "EXCEPTIONS_FILE",
        repo / "governance" / "security" / "temporary_exceptions.json",
    )
    monkeypatch.setattr(exception_path_metadata_gate, "WAIVERS_FILE", repo / "evidence" / "repro" / "waivers.json")
    monkeypatch.setattr(exception_path_metadata_gate, "evidence_root", lambda: ev)

    assert exception_path_metadata_gate.main([]) == 1
    report = json.loads((ev / "security" / "exception_path_metadata_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_owner:exception:0" in report["findings"]
    assert "missing_expiry:waiver:0" in report["findings"]
    assert "missing_justification:waiver:0" in report["findings"]
