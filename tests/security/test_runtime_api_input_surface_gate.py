from __future__ import annotations

import json
from pathlib import Path

from tooling.security import runtime_api_input_surface_gate


def _write_policy(repo: Path) -> None:
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security" / "runtime_api_input_surface_policy.json").write_text(
        json.dumps(
            {
                "request_schemas": ["submit_request"],
                "forbidden_property_fragments": ["path", "url", "uri"],
                "allowlisted_properties": [],
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_runtime_api_input_surface_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    (repo / "runtime" / "glyphser" / "api" / "schemas").mkdir(parents=True, exist_ok=True)
    (repo / "runtime" / "glyphser" / "api" / "schemas" / "runtime_api_schemas.json").write_text(
        json.dumps({"submit_request": {"properties": {"payload": {}, "scope": {}, "token": {}}}}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(runtime_api_input_surface_gate, "ROOT", repo)
    monkeypatch.setattr(runtime_api_input_surface_gate, "evidence_root", lambda: repo / "evidence")
    assert runtime_api_input_surface_gate.main([]) == 0


def test_runtime_api_input_surface_gate_fails_for_forbidden_property(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    (repo / "runtime" / "glyphser" / "api" / "schemas").mkdir(parents=True, exist_ok=True)
    (repo / "runtime" / "glyphser" / "api" / "schemas" / "runtime_api_schemas.json").write_text(
        json.dumps({"submit_request": {"properties": {"payload_path": {}, "scope": {}, "token": {}}}}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(runtime_api_input_surface_gate, "ROOT", repo)
    monkeypatch.setattr(runtime_api_input_surface_gate, "evidence_root", lambda: repo / "evidence")
    assert runtime_api_input_surface_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "runtime_api_input_surface_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("forbidden_property_fragment:") for item in report["findings"])
