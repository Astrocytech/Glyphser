from __future__ import annotations

import json
from pathlib import Path

from tooling.security import threat_control_mapping_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_threat_control_mapping_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)

    _write(
        repo / "tooling" / "security" / "security_super_gate_manifest.json",
        {"core": ["tooling/security/policy_signature_gate.py"], "extended": []},
    )
    _write(
        repo / "governance" / "security" / "metadata" / "THREAT_MODEL.meta.json",
        {"control_ids": ["CTRL-PROVENANCE-SIGNATURE"]},
    )
    _write(
        repo / "governance" / "security" / "threat_control_matrix.json",
        {
            "controls": [
                {
                    "id": "CTRL-PROVENANCE-SIGNATURE",
                    "threat": "tamper",
                    "owner": "security-team",
                    "gates": ["tooling/security/policy_signature_gate.py"],
                    "workflows": [".github/workflows/ci.yml"],
                    "evidence": ["evidence/security/policy_signature.json"],
                }
            ],
            "critical_gates": ["tooling/security/policy_signature_gate.py"],
        },
    )
    (repo / "tooling" / "security" / "policy_signature_gate.py").parent.mkdir(parents=True, exist_ok=True)
    (repo / "tooling" / "security" / "policy_signature_gate.py").write_text("print('ok')\n", encoding="utf-8")
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text(
        "jobs:\n  security:\n    steps:\n      - run: python tooling/security/policy_signature_gate.py\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(threat_control_mapping_gate, "ROOT", repo)
    monkeypatch.setattr(
        threat_control_mapping_gate,
        "MATRIX",
        repo / "governance" / "security" / "threat_control_matrix.json",
    )
    monkeypatch.setattr(
        threat_control_mapping_gate,
        "THREAT_META",
        repo / "governance" / "security" / "metadata" / "THREAT_MODEL.meta.json",
    )
    monkeypatch.setattr(
        threat_control_mapping_gate,
        "SUPER_MANIFEST",
        repo / "tooling" / "security" / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(threat_control_mapping_gate, "evidence_root", lambda: repo / "evidence")
    assert threat_control_mapping_gate.main([]) == 0


def test_threat_control_mapping_gate_fails_on_drift_and_missing_owner(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)

    _write(
        repo / "tooling" / "security" / "security_super_gate_manifest.json",
        {"core": [], "extended": []},
    )
    _write(
        repo / "governance" / "security" / "metadata" / "THREAT_MODEL.meta.json",
        {"control_ids": ["CTRL-ONE", "CTRL-TWO"]},
    )
    _write(
        repo / "governance" / "security" / "threat_control_matrix.json",
        {
            "controls": [
                {
                    "id": "CTRL-ONE",
                    "owner": "",
                    "gates": ["tooling/security/policy_signature_gate.py"],
                    "workflows": [".github/workflows/ci.yml"],
                    "evidence": ["evidence/security/policy_signature.json"],
                }
            ],
            "critical_gates": ["tooling/security/policy_signature_gate.py"],
        },
    )
    (repo / ".github" / "workflows").mkdir(parents=True, exist_ok=True)
    (repo / ".github" / "workflows" / "ci.yml").write_text("jobs:\n  test:\n    steps: []\n", encoding="utf-8")
    (repo / "tooling" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "tooling" / "security" / "policy_signature_gate.py").write_text("print('ok')\n", encoding="utf-8")

    monkeypatch.setattr(threat_control_mapping_gate, "ROOT", repo)
    monkeypatch.setattr(
        threat_control_mapping_gate,
        "MATRIX",
        repo / "governance" / "security" / "threat_control_matrix.json",
    )
    monkeypatch.setattr(
        threat_control_mapping_gate,
        "THREAT_META",
        repo / "governance" / "security" / "metadata" / "THREAT_MODEL.meta.json",
    )
    monkeypatch.setattr(
        threat_control_mapping_gate,
        "SUPER_MANIFEST",
        repo / "tooling" / "security" / "security_super_gate_manifest.json",
    )
    monkeypatch.setattr(threat_control_mapping_gate, "evidence_root", lambda: repo / "evidence")
    assert threat_control_mapping_gate.main([]) == 1
    report = json.loads((ev / "threat_control_mapping_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_owner:CTRL-ONE" in report["findings"]
    assert "threat_metadata_control_unmapped:CTRL-TWO" in report["findings"]
    assert "critical_gate_without_control_owner:tooling/security/policy_signature_gate.py" in report["findings"]
