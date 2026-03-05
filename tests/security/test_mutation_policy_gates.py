from __future__ import annotations

import hashlib
import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key
from tooling.security import evidence_attestation_gate, policy_signature_gate, provenance_signature_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_mutation_policy_signature_verification_condition(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "x.json"
    _write_json(policy, {"ok": True})
    (policy.with_suffix(".json.sig")).write_text("invalid\n", encoding="utf-8")
    _write_json(repo / "governance" / "security" / "policy_signature_manifest.json", {"policies": [str(policy.relative_to(repo))]})

    monkeypatch.setattr(policy_signature_gate, "ROOT", repo)
    monkeypatch.setattr(policy_signature_gate, "evidence_root", lambda: repo / "evidence")
    baseline = policy_signature_gate.main([])
    assert baseline == 1

    monkeypatch.setattr(policy_signature_gate, "_verify_with_allowed_keys", lambda p, s, strict_key: (True, "ok"))
    mutant = policy_signature_gate.main([])
    assert mutant == 0
    assert mutant != baseline


def test_mutation_provenance_signature_pair_verification_condition(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    for name in ("sbom.json", "build_provenance.json", "slsa_provenance_v1.json"):
        (sec / name).write_text("{}\n", encoding="utf-8")
        (sec / f"{name}.sig").write_text("bad\n", encoding="utf-8")

    monkeypatch.setattr(provenance_signature_gate, "ROOT", repo)
    monkeypatch.setattr(provenance_signature_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(provenance_signature_gate, "current_key", lambda strict=False: b"k")
    baseline = provenance_signature_gate.main([])
    assert baseline == 1

    monkeypatch.setattr(provenance_signature_gate, "_verify_pair", lambda path, sig_path, strict_key: (True, "ok"))
    mutant = provenance_signature_gate.main([])
    assert mutant == 0
    assert mutant != baseline


def test_mutation_evidence_attestation_signature_verification_condition(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    target = sec / "alpha.json"
    target.write_text("{}\n", encoding="utf-8")
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    index = sec / "evidence_attestation_index.json"
    _write_json(index, {"items": [{"seq": 1, "path": "evidence/security/alpha.json", "sha256": digest}]})
    (sec / "evidence_attestation_index.json.sig").write_text("bad\n", encoding="utf-8")

    monkeypatch.setattr(evidence_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(evidence_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(evidence_attestation_gate, "current_key", lambda strict=False: current_key(strict=False))
    baseline = evidence_attestation_gate.main([])
    assert baseline == 1

    monkeypatch.setattr(evidence_attestation_gate, "verify_file", lambda path, sig, key: True)
    mutant = evidence_attestation_gate.main([])
    assert mutant == 0
    assert mutant != baseline
