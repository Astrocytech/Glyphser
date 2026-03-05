from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import promotion_policy_gate


def _write_policy(repo: Path, *, allow_override: bool = True) -> None:
    policy = repo / "governance" / "security" / "promotion_policy.json"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        json.dumps(
            {
                "required_reports": [
                    "policy_signature.json",
                    "provenance_signature.json",
                    "evidence_attestation_gate.json",
                    "provenance_revocation_gate.json",
                ],
                "allow_signed_override": allow_override,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_promotion_policy_gate_passes_with_required_reports(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    for name in (
        "policy_signature.json",
        "provenance_signature.json",
        "evidence_attestation_gate.json",
        "provenance_revocation_gate.json",
    ):
        (sec / name).write_text(json.dumps({"status": "PASS"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(promotion_policy_gate, "ROOT", repo)
    monkeypatch.setattr(promotion_policy_gate, "POLICY", repo / "governance/security/promotion_policy.json")
    monkeypatch.setattr(promotion_policy_gate, "OVERRIDE", repo / "governance/security/promotion_override.json")
    monkeypatch.setattr(promotion_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert promotion_policy_gate.main([]) == 0


def test_promotion_policy_gate_fails_missing_required_report(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo)
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "policy_signature.json").write_text(json.dumps({"status": "PASS"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(promotion_policy_gate, "ROOT", repo)
    monkeypatch.setattr(promotion_policy_gate, "POLICY", repo / "governance/security/promotion_policy.json")
    monkeypatch.setattr(promotion_policy_gate, "OVERRIDE", repo / "governance/security/promotion_override.json")
    monkeypatch.setattr(promotion_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert promotion_policy_gate.main([]) == 1


def test_promotion_policy_gate_allows_valid_signed_override(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo, allow_override=True)
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    for name in (
        "policy_signature.json",
        "provenance_signature.json",
        "evidence_attestation_gate.json",
        "provenance_revocation_gate.json",
    ):
        (sec / name).write_text(json.dumps({"status": "FAIL"}) + "\n", encoding="utf-8")
    override = repo / "governance" / "security" / "promotion_override.json"
    override.parent.mkdir(parents=True, exist_ok=True)
    override.write_text(
        json.dumps(
            {
                "owner": "security-ops",
                "reason": "Emergency promotion override for incident response.",
                "expires_at_utc": "2099-01-01T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    override.with_suffix(".json.sig").write_text(
        sign_file(override, key=current_key(strict=False)) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(promotion_policy_gate, "ROOT", repo)
    monkeypatch.setattr(promotion_policy_gate, "POLICY", repo / "governance/security/promotion_policy.json")
    monkeypatch.setattr(promotion_policy_gate, "OVERRIDE", override)
    monkeypatch.setattr(promotion_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert promotion_policy_gate.main([]) == 0


def test_promotion_policy_gate_override_does_not_bypass_missing_mandatory_evidence(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo, allow_override=True)
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True, exist_ok=True)
    override = repo / "governance" / "security" / "promotion_override.json"
    override.parent.mkdir(parents=True, exist_ok=True)
    override.write_text(
        json.dumps(
            {
                "owner": "security-ops",
                "reason": "Emergency promotion override for incident response.",
                "expires_at_utc": "2099-01-01T00:00:00+00:00",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    override.with_suffix(".json.sig").write_text(
        sign_file(override, key=current_key(strict=False)) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(promotion_policy_gate, "ROOT", repo)
    monkeypatch.setattr(promotion_policy_gate, "POLICY", repo / "governance/security/promotion_policy.json")
    monkeypatch.setattr(promotion_policy_gate, "OVERRIDE", override)
    monkeypatch.setattr(promotion_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert promotion_policy_gate.main([]) == 1
