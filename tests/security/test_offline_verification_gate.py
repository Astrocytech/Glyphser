from __future__ import annotations

import json
from pathlib import Path

from tooling.security import offline_verification_gate


def test_offline_verification_gate_passes_with_valid_signatures(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True, exist_ok=True)
    pol = gov / "policy_a.json"
    pol.write_text('{"k":"v"}\n', encoding="utf-8")
    pol_sig = pol.with_suffix(".json.sig")
    pol_sig.write_text("sig\n", encoding="utf-8")
    (gov / "policy_signature_manifest.json").write_text(
        json.dumps({"policies": ["governance/security/policy_a.json"]}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(offline_verification_gate, "ROOT", repo)
    monkeypatch.setattr(offline_verification_gate, "MANIFEST", gov / "policy_signature_manifest.json")
    monkeypatch.setattr(offline_verification_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(offline_verification_gate, "current_key", lambda strict=False: "k")
    monkeypatch.setattr(offline_verification_gate, "bootstrap_key", lambda: "bk")
    monkeypatch.setattr(offline_verification_gate, "verify_file", lambda *_a, **_k: True)
    monkeypatch.setattr(offline_verification_gate, "verify_index", lambda strict_key=False: {"status": "PASS"})

    assert offline_verification_gate.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "offline_verification_gate.json").read_text("utf-8"))
    assert report["status"] == "PASS"


def test_offline_verification_gate_fails_when_manifest_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(offline_verification_gate, "ROOT", repo)
    monkeypatch.setattr(offline_verification_gate, "MANIFEST", gov / "policy_signature_manifest.json")
    monkeypatch.setattr(offline_verification_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(offline_verification_gate, "verify_index", lambda strict_key=False: {"status": "PASS"})

    assert offline_verification_gate.main([]) == 1
