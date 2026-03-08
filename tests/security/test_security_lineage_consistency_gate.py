from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_lineage_consistency_gate


def _write(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_security_lineage_consistency_gate_passes_when_all_consumed_artifacts_are_referenced(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    _write(
        sec / "security_super_gate.json",
        {
            "results": [
                {"cmd": ["python", "tooling/security/policy_signature_gate.py"], "status": "PASS"},
                {"cmd": ["python", "tooling/security/provenance_signature_gate.py"], "status": "PASS"},
            ]
        },
    )
    _write(
        sec / "security_lineage_map.json",
        {
            "mappings": [
                {
                    "report": "security/security_super_gate.json",
                    "field_path": "results[0].status",
                    "source_artifacts": ["security/policy_signature_gate.json"],
                    "rule_id": "LINEAGE_SUPER_GATE_COMPONENT_STATUS",
                },
                {
                    "report": "security/security_super_gate.json",
                    "field_path": "results[1].status",
                    "source_artifacts": ["security/provenance_signature_gate.json"],
                    "rule_id": "LINEAGE_SUPER_GATE_COMPONENT_STATUS",
                },
            ]
        },
    )
    monkeypatch.setattr(security_lineage_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(security_lineage_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_lineage_consistency_gate.main([]) == 0
    report = json.loads((sec / "security_lineage_consistency_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["missing_references"] == 0


def test_security_lineage_consistency_gate_fails_on_unreferenced_consumed_artifacts(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path
    sec = repo / "evidence" / "security"
    _write(
        sec / "security_super_gate.json",
        {
            "results": [
                {"cmd": ["python", "tooling/security/policy_signature_gate.py"], "status": "PASS"},
            ]
        },
    )
    _write(
        sec / "security_lineage_map.json",
        {"mappings": [{"report": "security/security_super_gate.json", "field_path": "status", "source_artifacts": []}]},
    )
    monkeypatch.setattr(security_lineage_consistency_gate, "ROOT", repo)
    monkeypatch.setattr(security_lineage_consistency_gate, "evidence_root", lambda: repo / "evidence")
    assert security_lineage_consistency_gate.main([]) == 1
    report = json.loads((sec / "security_lineage_consistency_gate.json").read_text(encoding="utf-8"))
    assert "missing_lineage_reference:security/policy_signature_gate.json" in report["findings"]
