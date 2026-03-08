from __future__ import annotations

import json
from pathlib import Path

from tooling.security import exported_security_evidence_api_contract_versioning_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, payloads: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(item) + "\n" for item in payloads), encoding="utf-8")


def _seed_policy(repo: Path) -> Path:
    policy = repo / "governance" / "security" / "exported_security_evidence_api_contract_policy.json"
    _write(
        policy,
        {
            "schema_version": 1,
            "current_api_contract_version": "v1",
            "allowed_versions": ["v1"],
            "required_exports": [
                {
                    "artifact": "evidence/security/security_dashboard.json",
                    "kind": "json",
                    "version_path": "metadata.api_contract_version",
                },
                {
                    "artifact": "evidence/security/security_events.jsonl",
                    "kind": "jsonl",
                    "version_field": "api_contract_version",
                },
                {
                    "artifact": "evidence/security/offline_verify_bundle_export.json",
                    "kind": "json",
                    "version_path": "metadata.api_contract_version",
                },
                {
                    "artifact": "evidence/security/offline_verify_bundle/export_manifest.json",
                    "kind": "json",
                    "version_path": "api_contract_version",
                },
            ],
        },
    )
    return policy


def test_exported_security_evidence_api_contract_versioning_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = _seed_policy(repo)
    _write(repo / "evidence" / "security" / "security_dashboard.json", {"metadata": {"api_contract_version": "v1"}})
    _write_jsonl(
        repo / "evidence" / "security" / "security_events.jsonl",
        [{"api_contract_version": "v1", "event_type": "security_gate_status"}],
    )
    _write(repo / "evidence" / "security" / "offline_verify_bundle_export.json", {"metadata": {"api_contract_version": "v1"}})
    _write(repo / "evidence" / "security" / "offline_verify_bundle" / "export_manifest.json", {"api_contract_version": "v1"})

    monkeypatch.setattr(exported_security_evidence_api_contract_versioning_gate, "ROOT", repo)
    monkeypatch.setattr(exported_security_evidence_api_contract_versioning_gate, "POLICY", policy)
    monkeypatch.setattr(exported_security_evidence_api_contract_versioning_gate, "evidence_root", lambda: repo / "evidence")
    assert exported_security_evidence_api_contract_versioning_gate.main([]) == 0


def test_exported_security_evidence_api_contract_versioning_gate_fails_on_missing_version(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = _seed_policy(repo)
    _write(repo / "evidence" / "security" / "security_dashboard.json", {"metadata": {"api_contract_version": "v1"}})
    _write_jsonl(
        repo / "evidence" / "security" / "security_events.jsonl",
        [{"event_type": "security_gate_status"}],
    )
    _write(repo / "evidence" / "security" / "offline_verify_bundle_export.json", {"metadata": {"api_contract_version": "v1"}})
    _write(repo / "evidence" / "security" / "offline_verify_bundle" / "export_manifest.json", {"api_contract_version": "v1"})

    monkeypatch.setattr(exported_security_evidence_api_contract_versioning_gate, "ROOT", repo)
    monkeypatch.setattr(exported_security_evidence_api_contract_versioning_gate, "POLICY", policy)
    monkeypatch.setattr(exported_security_evidence_api_contract_versioning_gate, "evidence_root", lambda: repo / "evidence")
    assert exported_security_evidence_api_contract_versioning_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "exported_security_evidence_api_contract_versioning_gate.json").read_text(
            encoding="utf-8"
        )
    )
    assert any(item.startswith("missing_api_contract_version:evidence/security/security_events.jsonl") for item in report["findings"])

