from __future__ import annotations

import json
from pathlib import Path

from tooling.security import external_export_data_minimization_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, payloads: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(item) + "\n" for item in payloads), encoding="utf-8")


def test_external_export_data_minimization_gate_passes_clean_exports(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    bundle = sec / "offline_verify_bundle"
    bundle.mkdir(parents=True, exist_ok=True)

    _write_json(sec / "security_dashboard.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write_jsonl(
        sec / "security_events.jsonl",
        [
            {
                "event_type": "security_gate_status",
                "severity": "high",
                "control_id": "gate_a",
                "run_id": "run-1",
                "artifact_ref": "evidence/security/gate_a.json",
                "urgency": "page",
            }
        ],
    )
    _write_json(
        sec / "offline_verify_bundle_export.json",
        {
            "status": "PASS",
            "findings": [],
            "summary": {
                "bundle_dir": "evidence/security/offline_verify_bundle",
                "exported_files": ["sbom.json"],
                "manifest": "evidence/security/offline_verify_bundle/export_manifest.json",
                "manifest_signature": "evidence/security/offline_verify_bundle/export_manifest.json.sig",
            },
            "metadata": {},
        },
    )
    _write_json(bundle / "export_manifest.json", {"package": "offline_verify_bundle", "files": []})

    monkeypatch.setattr(external_export_data_minimization_gate, "ROOT", repo)
    monkeypatch.setattr(external_export_data_minimization_gate, "evidence_root", lambda: repo / "evidence")
    assert external_export_data_minimization_gate.main([]) == 0


def test_external_export_data_minimization_gate_fails_on_sensitive_token_field(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    bundle = sec / "offline_verify_bundle"
    bundle.mkdir(parents=True, exist_ok=True)

    _write_json(sec / "security_dashboard.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write_jsonl(
        sec / "security_events.jsonl",
        [
            {
                "event_type": "security_gate_status",
                "severity": "high",
                "control_id": "gate_a",
                "run_id": "run-1",
                "artifact_ref": "evidence/security/gate_a.json",
                "api_token": "token-value-should-not-be-exported",
            }
        ],
    )
    _write_json(sec / "offline_verify_bundle_export.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})
    _write_json(bundle / "export_manifest.json", {"package": "offline_verify_bundle", "files": []})

    monkeypatch.setattr(external_export_data_minimization_gate, "ROOT", repo)
    monkeypatch.setattr(external_export_data_minimization_gate, "evidence_root", lambda: repo / "evidence")
    assert external_export_data_minimization_gate.main([]) == 1
    report = json.loads((sec / "external_export_data_minimization_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("sensitive_key:$[1].api_token") for item in report["findings"])

