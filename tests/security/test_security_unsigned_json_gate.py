from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_unsigned_json_gate


def _write_policy(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"required_signed_security_json": ["sbom.json", "build_provenance.json"]}) + "\n",
        encoding="utf-8",
    )


def test_security_unsigned_json_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write_policy(repo / "governance" / "security" / "security_artifact_signature_policy.json")
    (sec / "sbom.json").write_text("{}\n", encoding="utf-8")
    (sec / "sbom.json.sig").write_text("sig\n", encoding="utf-8")
    (sec / "build_provenance.json").write_text("{}\n", encoding="utf-8")
    (sec / "build_provenance.json.sig").write_text("sig\n", encoding="utf-8")
    monkeypatch.setattr(security_unsigned_json_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_unsigned_json_gate,
        "POLICY",
        repo / "governance" / "security" / "security_artifact_signature_policy.json",
    )
    monkeypatch.setattr(security_unsigned_json_gate, "evidence_root", lambda: repo / "evidence")
    assert security_unsigned_json_gate.main([]) == 0


def test_security_unsigned_json_gate_fails_missing_signature(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    _write_policy(repo / "governance" / "security" / "security_artifact_signature_policy.json")
    (sec / "sbom.json").write_text("{}\n", encoding="utf-8")
    (sec / "build_provenance.json").write_text("{}\n", encoding="utf-8")
    (sec / "build_provenance.json.sig").write_text("sig\n", encoding="utf-8")
    monkeypatch.setattr(security_unsigned_json_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_unsigned_json_gate,
        "POLICY",
        repo / "governance" / "security" / "security_artifact_signature_policy.json",
    )
    monkeypatch.setattr(security_unsigned_json_gate, "evidence_root", lambda: repo / "evidence")
    assert security_unsigned_json_gate.main([]) == 1
    report = json.loads((sec / "security_unsigned_json_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "required_artifact_signature_missing:sbom.json" in report["findings"]
