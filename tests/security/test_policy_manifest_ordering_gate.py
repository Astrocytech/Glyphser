from __future__ import annotations

import json
from pathlib import Path

from tooling.security import policy_manifest_ordering_gate


def test_policy_manifest_ordering_gate_passes_for_sorted_manifest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    gov.mkdir(parents=True, exist_ok=True)
    manifest = gov / "policy_signature_manifest.json"
    manifest.write_text(
        json.dumps({"policies": ["governance/security/a.json", "governance/security/b.json"]}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(policy_manifest_ordering_gate, "ROOT", repo)
    monkeypatch.setattr(policy_manifest_ordering_gate, "MANIFEST", manifest)
    monkeypatch.setattr(policy_manifest_ordering_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_manifest_ordering_gate.main([]) == 0


def test_policy_manifest_ordering_gate_fails_for_unsorted_manifest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    ev = repo / "evidence" / "security"
    gov.mkdir(parents=True, exist_ok=True)
    ev.mkdir(parents=True, exist_ok=True)
    manifest = gov / "policy_signature_manifest.json"
    manifest.write_text(
        json.dumps({"policies": ["governance/security/b.json", "governance/security/a.json"]}) + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(policy_manifest_ordering_gate, "ROOT", repo)
    monkeypatch.setattr(policy_manifest_ordering_gate, "MANIFEST", manifest)
    monkeypatch.setattr(policy_manifest_ordering_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_manifest_ordering_gate.main([]) == 1
    report = json.loads((ev / "policy_manifest_ordering_gate.json").read_text(encoding="utf-8"))
    assert "policy_manifest_not_sorted_lexicographically" in report["findings"]


def test_policy_manifest_ordering_gate_enforces_canonical_normalized_order(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    gov = repo / "governance" / "security"
    ev = repo / "evidence" / "security"
    gov.mkdir(parents=True, exist_ok=True)
    ev.mkdir(parents=True, exist_ok=True)
    manifest = gov / "policy_signature_manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "policies": [
                    "governance/security/z.json",
                    "governance\\security\\a.json ",
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(policy_manifest_ordering_gate, "ROOT", repo)
    monkeypatch.setattr(policy_manifest_ordering_gate, "MANIFEST", manifest)
    monkeypatch.setattr(policy_manifest_ordering_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_manifest_ordering_gate.main([]) == 1
    report = json.loads((ev / "policy_manifest_ordering_gate.json").read_text(encoding="utf-8"))
    assert "non_canonical_policy_entry:1" in report["findings"]
    assert "policy_manifest_not_sorted_lexicographically" in report["findings"]
