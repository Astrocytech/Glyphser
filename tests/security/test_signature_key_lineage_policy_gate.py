from __future__ import annotations

import json
from pathlib import Path

from tooling.security import signature_key_lineage_policy_gate


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def test_signature_key_lineage_policy_gate_passes_when_required_fields_match(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    policy = repo / "governance" / "security" / "signature_key_lineage_policy.json"
    _write(
        policy,
        {
            "required_pairs": [
                {
                    "left": "policy_signature",
                    "right": "provenance_signature",
                    "must_match_fields": ["key_id", "adapter", "source"],
                }
            ]
        },
    )
    key_provenance = {"key_id": "kid-1", "adapter": "hmac", "source": "env"}
    _write(sec / "policy_signature.json", {"metadata": {"key_provenance": key_provenance}})
    _write(sec / "provenance_signature.json", {"metadata": {"key_provenance": key_provenance}})

    monkeypatch.setattr(signature_key_lineage_policy_gate, "ROOT", repo)
    monkeypatch.setattr(signature_key_lineage_policy_gate, "POLICY", policy)
    monkeypatch.setattr(signature_key_lineage_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert signature_key_lineage_policy_gate.main([]) == 0


def test_signature_key_lineage_policy_gate_fails_on_lineage_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    policy = repo / "governance" / "security" / "signature_key_lineage_policy.json"
    _write(
        policy,
        {
            "required_pairs": [
                {
                    "left": "policy_signature",
                    "right": "provenance_signature",
                    "must_match_fields": ["key_id"],
                }
            ]
        },
    )
    _write(sec / "policy_signature.json", {"metadata": {"key_provenance": {"key_id": "kid-a"}}})
    _write(sec / "provenance_signature.json", {"metadata": {"key_provenance": {"key_id": "kid-b"}}})

    monkeypatch.setattr(signature_key_lineage_policy_gate, "ROOT", repo)
    monkeypatch.setattr(signature_key_lineage_policy_gate, "POLICY", policy)
    monkeypatch.setattr(signature_key_lineage_policy_gate, "evidence_root", lambda: repo / "evidence")
    assert signature_key_lineage_policy_gate.main([]) == 1
    report = json.loads((sec / "signature_key_lineage_policy_gate.json").read_text(encoding="utf-8"))
    assert "key_lineage_mismatch:policy_signature:provenance_signature:key_id:kid-a!=kid-b" in report["findings"]
