from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from tooling.security import export_offline_verify_bundle, security_dashboard_export, security_event_export


CONTRACTS: dict[str, dict[str, Any]] = {
    "dashboard_ingest_v1": {
        "required": {"status": str, "findings": list, "summary": dict, "metadata": dict},
        "compatibility": "additive_only",
    },
    "siem_ingest_v1": {
        "required": {
            "event_type": str,
            "severity": str,
            "control_id": str,
            "run_id": str,
            "artifact_ref": str,
        },
        "compatibility": "additive_only",
    },
    "audit_export_ingest_v1": {
        "required": {"status": str, "findings": list, "summary": dict, "metadata": dict},
        "required_summary": {"bundle_dir": str, "exported_files": list, "manifest": str, "manifest_signature": str},
        "compatibility": "additive_only",
    },
}


def _write(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _assert_contract(payload: dict[str, Any], contract: dict[str, Any]) -> None:
    for field, expected_type in contract["required"].items():
        assert field in payload
        assert isinstance(payload[field], expected_type)
    for field, expected_type in contract.get("required_summary", {}).items():
        assert field in payload["summary"]
        assert isinstance(payload["summary"][field], expected_type)


def _assert_additive_compatibility(
    legacy_contract: dict[str, Any], current_contract: dict[str, Any], legacy_payload: dict[str, Any]
) -> None:
    assert current_contract["compatibility"] == "additive_only"
    assert set(current_contract["required"]).issubset(set(legacy_contract["required"]))
    assert set(current_contract.get("required_summary", {})).issubset(set(legacy_contract.get("required_summary", {})))
    _assert_contract(legacy_payload, legacy_contract)


def _seed_export_inputs(repo: Path) -> None:
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    gov.mkdir(parents=True, exist_ok=True)

    _write(sec / "policy_signature.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write(sec / "provenance_signature.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write(sec / "evidence_attestation_gate.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write(sec / "security_slo_report.json", {"status": "PASS", "findings": [], "summary": {"pass_rate": 1.0}, "metadata": {}})
    _write(sec / "some_warn_gate.json", {"status": "WARN", "findings": ["warn"], "summary": {}, "metadata": {}})
    _write(sec / "some_fail_gate.json", {"status": "FAIL", "findings": ["fail"], "summary": {}, "metadata": {}})
    _write(gov / "incident_response_policy.json", {"alert_routing_test": {"primary_contact": "soc@example.test"}})

    _write(gov / "policy_signature_manifest.json", {"policies": []})
    (gov / "policy_signature_manifest.json.sig").write_text("sig\n", encoding="utf-8")
    _write(gov / "provenance_revocation_list.json", {"revocations": []})
    (gov / "provenance_revocation_list.json.sig").write_text("sig\n", encoding="utf-8")
    _write(sec / "build_provenance.json", {"status": "ok"})
    (sec / "build_provenance.json.sig").write_text("sig\n", encoding="utf-8")
    _write(sec / "sbom.json", {"packages": []})
    (sec / "sbom.json.sig").write_text("sig\n", encoding="utf-8")
    _write(sec / "evidence_chain_of_custody.json", {"items": []})
    (sec / "evidence_chain_of_custody.json.sig").write_text("sig\n", encoding="utf-8")


def test_external_ingestion_contracts_accept_current_exports(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_export_inputs(repo)
    sec = repo / "evidence" / "security"
    gov = repo / "governance" / "security"

    monkeypatch.setenv("GLYPHSER_RUN_ID", "run-contract")
    monkeypatch.setattr(security_dashboard_export, "ROOT", repo)
    monkeypatch.setattr(security_dashboard_export, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_event_export, "ROOT", repo)
    monkeypatch.setattr(security_event_export, "INCIDENT_POLICY", gov / "incident_response_policy.json")
    monkeypatch.setattr(security_event_export, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(export_offline_verify_bundle, "ROOT", repo)
    monkeypatch.setattr(export_offline_verify_bundle, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(
        export_offline_verify_bundle,
        "load_policy",
        lambda: {"offline_bundle_dir": "evidence/security/offline_verify_bundle"},
    )

    assert security_dashboard_export.main([]) == 0
    assert security_event_export.main([]) == 0
    assert export_offline_verify_bundle.main([]) == 0

    dashboard = json.loads((sec / "security_dashboard.json").read_text(encoding="utf-8"))
    _assert_contract(dashboard, CONTRACTS["dashboard_ingest_v1"])

    siem_lines = (sec / "security_events.jsonl").read_text(encoding="utf-8").splitlines()
    assert siem_lines
    for line in siem_lines:
        _assert_contract(json.loads(line), CONTRACTS["siem_ingest_v1"])

    audit_export = json.loads((sec / "offline_verify_bundle_export.json").read_text(encoding="utf-8"))
    _assert_contract(audit_export, CONTRACTS["audit_export_ingest_v1"])


def test_external_ingestion_contracts_remain_backward_compatible() -> None:
    legacy_dashboard_contract = {
        "required": {"status": str, "findings": list, "summary": dict, "metadata": dict},
        "compatibility": "additive_only",
    }
    legacy_siem_contract = {
        "required": {
            "event_type": str,
            "severity": str,
            "control_id": str,
            "run_id": str,
            "artifact_ref": str,
        },
        "compatibility": "additive_only",
    }
    legacy_audit_contract = {
        "required": {"status": str, "findings": list, "summary": dict, "metadata": dict},
        "required_summary": {"bundle_dir": str, "exported_files": list, "manifest": str, "manifest_signature": str},
        "compatibility": "additive_only",
    }

    legacy_dashboard_payload = {"status": "PASS", "findings": [], "summary": {}, "metadata": {}}
    legacy_siem_payload = {
        "event_type": "security_gate_status",
        "severity": "medium",
        "control_id": "gate",
        "run_id": "run-1",
        "artifact_ref": "evidence/security/gate.json",
    }
    legacy_audit_payload = {
        "status": "PASS",
        "findings": [],
        "summary": {
            "bundle_dir": "evidence/security/offline_verify_bundle",
            "exported_files": [],
            "manifest": "evidence/security/offline_verify_bundle/export_manifest.json",
            "manifest_signature": "evidence/security/offline_verify_bundle/export_manifest.json.sig",
        },
        "metadata": {},
    }

    _assert_additive_compatibility(legacy_dashboard_contract, CONTRACTS["dashboard_ingest_v1"], legacy_dashboard_payload)
    _assert_additive_compatibility(legacy_siem_contract, CONTRACTS["siem_ingest_v1"], legacy_siem_payload)
    _assert_additive_compatibility(legacy_audit_contract, CONTRACTS["audit_export_ingest_v1"], legacy_audit_payload)
