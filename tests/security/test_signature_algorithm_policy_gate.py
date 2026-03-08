from __future__ import annotations

import json
from pathlib import Path

from tooling.security import signature_algorithm_policy_gate


def _write(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _policy(repo: Path, *, forbidden: list[str], allowed: list[str]) -> None:
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security" / "advanced_hardening_policy.json").write_text(
        json.dumps(
            {
                "forbidden_signature_adapters": forbidden,
                "allowed_signature_adapters": allowed,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_signature_algorithm_policy_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _policy(repo, forbidden=["md5", "sha1", "none"], allowed=["hmac", "kms"])
    _write(sec / "policy_signature.json", {"metadata": {"key_provenance": {"adapter": "hmac"}}})
    _write(sec / "provenance_signature.json", {"metadata": {"key_provenance": {"adapter": "hmac"}}})
    _write(sec / "evidence_attestation_index.json", {"key_provenance": {"adapter": "hmac"}})
    monkeypatch.setattr(signature_algorithm_policy_gate, "ROOT", repo)
    monkeypatch.setattr(signature_algorithm_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert signature_algorithm_policy_gate.main([]) == 0


def test_signature_algorithm_policy_gate_fails_on_forbidden_or_unallowlisted(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    _policy(repo, forbidden=["none", "sha1"], allowed=["hmac", "kms"])
    _write(sec / "policy_signature.json", {"metadata": {"key_provenance": {"adapter": "none"}}})
    _write(sec / "provenance_signature.json", {"metadata": {"key_provenance": {"adapter": "ed25519"}}})
    _write(sec / "evidence_attestation_index.json", {"key_provenance": {"adapter": "kms"}})
    monkeypatch.setattr(signature_algorithm_policy_gate, "ROOT", repo)
    monkeypatch.setattr(signature_algorithm_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert signature_algorithm_policy_gate.main([]) == 1
    report = json.loads((sec / "signature_algorithm_policy_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("forbidden_signature_adapter:") for item in report["findings"])
    assert any(str(item).startswith("signature_adapter_not_allowlisted:") for item in report["findings"])
