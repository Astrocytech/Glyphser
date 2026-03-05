from __future__ import annotations

import json
from pathlib import Path

from tooling.security import (
    security_event_schema_gate,
    security_report_schema_contract_gate,
    security_schema_compatibility_policy_gate,
    upload_manifest_completeness_gate,
)


def _oversized_object(size: int = 12000) -> dict[str, object]:
    return {f"k{i:05d}": i for i in range(size)}


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_oversized_json_keycount_stress_for_policy_and_report_parsers(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    oversized = _oversized_object()

    contract = repo / "governance" / "security" / "security_report_schema_contract.json"
    policy = repo / "governance" / "security" / "security_schema_compatibility_policy.json"
    _write_json(contract, oversized)
    _write_json(policy, oversized)

    monkeypatch.setattr(security_report_schema_contract_gate, "ROOT", repo)
    monkeypatch.setattr(security_report_schema_contract_gate, "CONTRACT", contract)
    monkeypatch.setattr(security_report_schema_contract_gate, "evidence_root", lambda: repo / "evidence")
    assert security_report_schema_contract_gate.main([]) == 1

    monkeypatch.setattr(security_schema_compatibility_policy_gate, "ROOT", repo)
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "POLICY", policy)
    monkeypatch.setattr(security_schema_compatibility_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert security_schema_compatibility_policy_gate.main([]) == 1

    assert (repo / "evidence" / "security" / "security_report_schema_contract_gate.json").exists()
    assert (repo / "evidence" / "security" / "security_schema_compatibility_policy_gate.json").exists()


def test_oversized_json_keycount_stress_for_event_and_manifest_parsers(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)

    schema = repo / "governance" / "security" / "security_event_schema.json"
    _write_json(
        schema,
        {
            "required_fields": ["event_type", "severity", "control_id", "run_id", "artifact_ref"],
            "allowed_severities": ["low", "medium", "high"],
            "event_type": "security_gate_status",
        },
    )
    oversized_event = _oversized_object()
    oversized_event.update(
        {
            "event_type": "security_gate_status",
            "severity": "high",
            "control_id": "gate",
            "run_id": "r1",
            "artifact_ref": "evidence/security/gate.json",
        }
    )
    (sec / "security_events.jsonl").write_text(json.dumps(oversized_event) + "\n", encoding="utf-8")

    monkeypatch.setattr(security_event_schema_gate, "ROOT", repo)
    monkeypatch.setattr(security_event_schema_gate, "SCHEMA", schema)
    monkeypatch.setattr(security_event_schema_gate, "evidence_root", lambda: repo / "evidence")
    assert security_event_schema_gate.main([]) == 0

    _write_json(sec / "upload_manifest.json", oversized_event)
    (sec / "upload_manifest.json.sig").write_text("bogus-signature\n", encoding="utf-8")
    monkeypatch.setattr(upload_manifest_completeness_gate, "ROOT", repo)
    monkeypatch.setattr(upload_manifest_completeness_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(upload_manifest_completeness_gate, "load_policy", lambda: {"security_workflow_evidence_required": []})
    monkeypatch.setattr(upload_manifest_completeness_gate, "verify_file", lambda *_a, **_k: False)
    assert upload_manifest_completeness_gate.main([]) == 1

    assert (sec / "security_event_schema_gate.json").exists()
    assert (sec / "upload_manifest_completeness_gate.json").exists()

