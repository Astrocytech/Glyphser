from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import sign_file
from tooling.security import provenance_signature_gate


def test_provenance_signature_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    sbom = sec / "sbom.json"
    prov = sec / "build_provenance.json"
    sbom.write_text('{"status":"ok"}\n', encoding="utf-8")
    prov.write_text('{"status":"ok"}\n', encoding="utf-8")
    key = b"test-key"
    (sec / "sbom.json.sig").write_text(sign_file(sbom, key=key) + "\n", encoding="utf-8")
    (sec / "build_provenance.json.sig").write_text(sign_file(prov, key=key) + "\n", encoding="utf-8")

    monkeypatch.setattr(provenance_signature_gate, "ROOT", repo)
    monkeypatch.setattr(provenance_signature_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(provenance_signature_gate, "current_key", lambda: key)

    rc = provenance_signature_gate.main()
    assert rc == 0
    report = json.loads((sec / "provenance_signature.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"


def test_provenance_signature_gate_fails_on_tamper(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    sbom = sec / "sbom.json"
    prov = sec / "build_provenance.json"
    sbom.write_text('{"status":"ok"}\n', encoding="utf-8")
    prov.write_text('{"status":"ok"}\n', encoding="utf-8")
    key = b"test-key"
    (sec / "sbom.json.sig").write_text(sign_file(sbom, key=key) + "\n", encoding="utf-8")
    (sec / "build_provenance.json.sig").write_text(sign_file(prov, key=key) + "\n", encoding="utf-8")
    sbom.write_text('{"status":"tampered"}\n', encoding="utf-8")

    monkeypatch.setattr(provenance_signature_gate, "ROOT", repo)
    monkeypatch.setattr(provenance_signature_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(provenance_signature_gate, "current_key", lambda: key)

    rc = provenance_signature_gate.main()
    assert rc == 1
    report = json.loads((sec / "provenance_signature.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
