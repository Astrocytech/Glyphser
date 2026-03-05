from __future__ import annotations

import json
from types import SimpleNamespace
from pathlib import Path

from tooling.security import external_audit_simulation


def test_external_audit_simulation_writes_closure_artifact(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(external_audit_simulation, "ROOT", repo)
    monkeypatch.setattr(external_audit_simulation, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        external_audit_simulation,
        "load_policy",
        lambda: {"offline_bundle_dir": "evidence/security/offline_verify_bundle", "storage_location": "immutable://store"},
    )
    monkeypatch.setattr(
        external_audit_simulation,
        "run_checked",
        lambda *args, **kwargs: SimpleNamespace(returncode=0, exit_reason="exit"),
    )

    assert external_audit_simulation.main(["--audit-id", "AUD-1"]) == 0
    report = json.loads((repo / "evidence" / "security" / "external_audit_simulation.json").read_text("utf-8"))
    closure = json.loads((repo / "evidence" / "security" / "external_audit_simulation_closure.json").read_text("utf-8"))
    assert report["status"] == "PASS"
    assert closure["status"] == "PASS"
    assert closure["incident_id"] == "AUD-1"
    assert all(item["verified"] is True for item in closure["action_items"])


def test_external_audit_simulation_fails_when_any_step_fails(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(external_audit_simulation, "ROOT", repo)
    monkeypatch.setattr(external_audit_simulation, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        external_audit_simulation,
        "load_policy",
        lambda: {"offline_bundle_dir": "evidence/security/offline_verify_bundle", "storage_location": "immutable://store"},
    )
    calls = {"n": 0}

    def _run(*args, **kwargs):
        calls["n"] += 1
        if calls["n"] == 2:
            return SimpleNamespace(returncode=2, exit_reason="exit")
        return SimpleNamespace(returncode=0, exit_reason="exit")

    monkeypatch.setattr(external_audit_simulation, "run_checked", _run)

    assert external_audit_simulation.main(["--audit-id", "AUD-2"]) == 1
    closure = json.loads((repo / "evidence" / "security" / "external_audit_simulation_closure.json").read_text("utf-8"))
    assert closure["status"] == "FAIL"
    assert any(item["verified"] is False for item in closure["action_items"])
