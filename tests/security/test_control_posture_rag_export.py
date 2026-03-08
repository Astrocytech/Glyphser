from __future__ import annotations

import json
from pathlib import Path

from tooling.security import control_posture_rag_export


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_control_posture_rag_export_passes_when_all_controls_green(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    for rel in (
        "security/security_super_gate.json",
        "security/policy_signature.json",
        "security/provenance_signature.json",
        "security/evidence_attestation_gate.json",
    ):
        _write(ev / rel, {"status": "PASS"})
    monkeypatch.setattr(control_posture_rag_export, "ROOT", repo)
    monkeypatch.setattr(control_posture_rag_export, "evidence_root", lambda: ev)
    assert control_posture_rag_export.main([]) == 0
    report = json.loads((ev / "security" / "control_posture_rag_export.json").read_text(encoding="utf-8"))
    assert report["summary"]["overall_rag"] == "green"


def test_control_posture_rag_export_fails_with_red_control(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    ev = repo / "evidence"
    _write(ev / "security" / "security_super_gate.json", {"status": "PASS"})
    _write(ev / "security" / "policy_signature.json", {"status": "FAIL"})
    _write(ev / "security" / "provenance_signature.json", {"status": "PASS"})
    _write(ev / "security" / "evidence_attestation_gate.json", {"status": "PASS"})
    monkeypatch.setattr(control_posture_rag_export, "ROOT", repo)
    monkeypatch.setattr(control_posture_rag_export, "evidence_root", lambda: ev)
    assert control_posture_rag_export.main([]) == 1
    report = json.loads((ev / "security" / "control_posture_rag_export.json").read_text(encoding="utf-8"))
    assert report["summary"]["overall_rag"] == "red"
