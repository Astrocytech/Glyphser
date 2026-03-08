from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import branch_protection_api_unavailability_drill


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_branch_protection_api_unavailability_drill_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    drill = repo / "governance" / "security" / "branch_protection_api_unavailability_drill.json"
    _write(
        drill,
        {
            "status": "PASS",
            "incident_id": "INC-1",
            "simulated_api_error": "github_api_503",
            "expected_gate_behavior": "Fail closed and emit evidence.",
            "observed_gate_status": "FAIL",
            "fail_closed": True,
            "emitted_evidence": "evidence/security/branch_protection_live.json",
        },
    )
    _sign(drill)

    monkeypatch.setattr(branch_protection_api_unavailability_drill, "ROOT", repo)
    monkeypatch.setattr(branch_protection_api_unavailability_drill, "DRILL", drill)
    monkeypatch.setattr(branch_protection_api_unavailability_drill, "evidence_root", lambda: repo / "evidence")
    assert branch_protection_api_unavailability_drill.main([]) == 0


def test_branch_protection_api_unavailability_drill_fails_on_missing_requirements(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    drill = repo / "governance" / "security" / "branch_protection_api_unavailability_drill.json"
    _write(
        drill,
        {
            "status": "FAIL",
            "incident_id": "",
            "simulated_api_error": "",
            "expected_gate_behavior": "",
            "observed_gate_status": "PASS",
            "fail_closed": False,
            "emitted_evidence": "",
        },
    )
    _sign(drill)

    monkeypatch.setattr(branch_protection_api_unavailability_drill, "ROOT", repo)
    monkeypatch.setattr(branch_protection_api_unavailability_drill, "DRILL", drill)
    monkeypatch.setattr(branch_protection_api_unavailability_drill, "evidence_root", lambda: repo / "evidence")
    assert branch_protection_api_unavailability_drill.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "branch_protection_api_unavailability_drill.json").read_text(encoding="utf-8")
    )
    assert "missing_incident_id" in report["findings"]
    assert "missing_simulated_api_error" in report["findings"]
    assert "invalid_observed_gate_status:PASS" in report["findings"]
    assert "gate_did_not_fail_closed" in report["findings"]
