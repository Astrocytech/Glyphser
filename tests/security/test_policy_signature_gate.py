from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import policy_signature_gate


def test_policy_signature_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    policy = gov / "a_policy.json"
    policy.write_text(json.dumps({"x": 1}) + "\n", encoding="utf-8")
    (gov / "policy_signature_manifest.json").write_text(
        json.dumps({"policies": ["governance/security/a_policy.json"]}) + "\n",
        encoding="utf-8",
    )
    (policy.with_suffix(".json.sig")).write_text(
        sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(policy_signature_gate, "ROOT", repo)
    monkeypatch.setattr(policy_signature_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_signature_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "policy_signature.json").read_text(encoding="utf-8"))
    assert "key_provenance" in report["metadata"]


def test_policy_signature_gate_fails_on_tamper(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    policy = gov / "a_policy.json"
    policy.write_text(json.dumps({"x": 1}) + "\n", encoding="utf-8")
    (gov / "policy_signature_manifest.json").write_text(
        json.dumps({"policies": ["governance/security/a_policy.json"]}) + "\n",
        encoding="utf-8",
    )
    sig_path = policy.with_suffix(".json.sig")
    sig_path.write_text(sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8")
    policy.write_text(json.dumps({"x": 2}) + "\n", encoding="utf-8")
    monkeypatch.setattr(policy_signature_gate, "ROOT", repo)
    monkeypatch.setattr(policy_signature_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_signature_gate.main([]) == 1


def test_policy_signature_gate_strict_mode_accepts_bootstrap_signed_policies(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True)
    policy = gov / "a_policy.json"
    policy.write_text(json.dumps({"x": 1}) + "\n", encoding="utf-8")
    (gov / "policy_signature_manifest.json").write_text(
        json.dumps({"policies": ["governance/security/a_policy.json"]}) + "\n",
        encoding="utf-8",
    )
    (policy.with_suffix(".json.sig")).write_text(
        sign_file(policy, key=current_key(strict=False)) + "\n", encoding="utf-8"
    )
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "strict-env-key")
    monkeypatch.setattr(policy_signature_gate, "ROOT", repo)
    monkeypatch.setattr(policy_signature_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_signature_gate.main(["--strict-key"]) == 0
