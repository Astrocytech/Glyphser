from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tooling.security import slsa_attestation_gate


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_slsa_attestation_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    sbom = sec / "sbom.json"
    prov = sec / "build_provenance.json"
    sbom.write_text('{"x":1}\n', encoding="utf-8")
    prov.write_text('{"x":2}\n', encoding="utf-8")
    att = {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://slsa.dev/provenance/v1",
        "subject": [
            {"name": "evidence/security/sbom.json", "digest": {"sha256": _sha(sbom)}},
            {"name": "evidence/security/build_provenance.json", "digest": {"sha256": _sha(prov)}},
        ],
        "predicate": {"runDetails": {"builder": {"id": "glyphser-ci"}}},
    }
    (sec / "slsa_provenance_v1.json").write_text(json.dumps(att) + "\n", encoding="utf-8")
    monkeypatch.setattr(slsa_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(slsa_attestation_gate, "evidence_root", lambda: repo / "evidence")
    assert slsa_attestation_gate.main() == 0


def test_slsa_attestation_gate_fails_on_bad_digest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    (sec / "sbom.json").write_text('{"x":1}\n', encoding="utf-8")
    (sec / "build_provenance.json").write_text('{"x":2}\n', encoding="utf-8")
    att = {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://slsa.dev/provenance/v1",
        "subject": [
            {"name": "evidence/security/sbom.json", "digest": {"sha256": "deadbeef"}},
            {"name": "evidence/security/build_provenance.json", "digest": {"sha256": "deadbeef"}},
        ],
        "predicate": {"runDetails": {"builder": {"id": "glyphser-ci"}}},
    }
    (sec / "slsa_provenance_v1.json").write_text(json.dumps(att) + "\n", encoding="utf-8")
    monkeypatch.setattr(slsa_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(slsa_attestation_gate, "evidence_root", lambda: repo / "evidence")
    assert slsa_attestation_gate.main() == 1
