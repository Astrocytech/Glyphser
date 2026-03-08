from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import verify_file
from tooling.security import export_offline_verify_bundle, security_dashboard_export, security_event_export


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _consume_dashboard(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["status"] == "PASS"
    summary = data["summary"]
    for key in ("policy_signature", "provenance_signature", "attestation"):
        assert summary[key] in {"PASS", "WARN", "FAIL", "MISSING"}
    return summary


def _consume_siem(path: Path) -> list[dict]:
    events = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert events
    for event in events:
        assert event["event_type"] == "security_gate_status"
        assert event["severity"] in {"low", "medium", "high"}
        assert event["control_id"]
        assert event["run_id"]
        assert event["artifact_ref"].startswith("evidence/security/")
    return events


def _consume_audit_export(bundle_dir: Path) -> set[str]:
    exported = {path.name for path in bundle_dir.iterdir() if path.is_file()}
    required_payloads = {
        "policy_signature_manifest.json",
        "provenance_revocation_list.json",
        "build_provenance.json",
        "sbom.json",
        "evidence_chain_of_custody.json",
    }
    for payload in required_payloads:
        assert payload in exported
        assert f"{payload}.sig" in exported
    assert "export_manifest.json" in exported
    assert "export_manifest.json.sig" in exported
    assert verify_file(
        bundle_dir / "export_manifest.json",
        (bundle_dir / "export_manifest.json.sig").read_text(encoding="utf-8").strip(),
        key=b"glyphser-provenance-hmac-fallback-v1",
    )
    assert "VERIFY.txt" in exported
    return exported


def test_downstream_consumers_ingest_exported_security_artifacts(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True, exist_ok=True)

    _write(sec / "policy_signature.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write(sec / "provenance_signature.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write(sec / "evidence_attestation_gate.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write(sec / "security_slo_report.json", {"status": "PASS", "findings": [], "summary": {"pass_rate": 1.0}, "metadata": {}})
    _write(sec / "security_super_gate.json", {"status": "WARN", "findings": ["x"], "summary": {}, "metadata": {}})
    _write(sec / "policy_signature_gate.json", {"status": "FAIL", "findings": ["x"], "summary": {}, "metadata": {}})
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

    monkeypatch.setenv("GLYPHSER_RUN_ID", "run-integration")
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

    dashboard_summary = _consume_dashboard(sec / "security_dashboard.json")
    assert dashboard_summary["slo"]["pass_rate"] == 1.0

    events = _consume_siem(sec / "security_events.jsonl")
    control_ids = {event["control_id"] for event in events}
    assert {"security_super_gate", "policy_signature_gate"}.issubset(control_ids)

    exported = _consume_audit_export(sec / "offline_verify_bundle")
    assert "sbom.json" in exported
