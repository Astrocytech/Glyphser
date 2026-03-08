from __future__ import annotations

import json
from pathlib import Path

from tooling.security import external_artifact_trust_contract_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_external_artifact_trust_contract_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(
        repo / "governance" / "security" / "external_artifact_trust_contract.json",
        {
            "contract_id": "v1",
            "owner": "security",
            "reviewed_at_utc": "2026-03-05T00:00:00+00:00",
            "accepted_repositories": ["github.com/example/a"],
            "required_attestations": ["provenance_signature"],
            "required_signer_identity_match": True,
        },
    )
    monkeypatch.setattr(external_artifact_trust_contract_gate, "ROOT", repo)
    monkeypatch.setattr(
        external_artifact_trust_contract_gate,
        "CONTRACT",
        repo / "governance" / "security" / "external_artifact_trust_contract.json",
    )
    monkeypatch.setattr(external_artifact_trust_contract_gate, "evidence_root", lambda: ev)
    assert external_artifact_trust_contract_gate.main([]) == 0


def test_external_artifact_trust_contract_gate_fails_on_invalid_contract(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(
        repo / "governance" / "security" / "external_artifact_trust_contract.json",
        {"owner": "security", "required_signer_identity_match": "yes"},
    )
    monkeypatch.setattr(external_artifact_trust_contract_gate, "ROOT", repo)
    monkeypatch.setattr(
        external_artifact_trust_contract_gate,
        "CONTRACT",
        repo / "governance" / "security" / "external_artifact_trust_contract.json",
    )
    monkeypatch.setattr(external_artifact_trust_contract_gate, "evidence_root", lambda: ev)
    assert external_artifact_trust_contract_gate.main([]) == 1
    report = json.loads((ev / "security" / "external_artifact_trust_contract_gate.json").read_text(encoding="utf-8"))
    assert "missing_field:contract_id" in report["findings"]
