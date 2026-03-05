from __future__ import annotations

import json
from pathlib import Path

from tooling.security import signed_policy_metadata_gate


def test_signed_policy_metadata_gate_passes_with_owner_and_review(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    pol = repo / "governance" / "security"
    ev.mkdir(parents=True)
    pol.mkdir(parents=True)
    (pol / "policy_signature_manifest.json").write_text(
        json.dumps({"policies": ["governance/security/p1.json"]}) + "\n", encoding="utf-8"
    )
    (pol / "p1.json").write_text(
        json.dumps({"owner": "sec-team", "last_reviewed_utc": "2026-03-04T00:00:00+00:00"}) + "\n", encoding="utf-8"
    )
    monkeypatch.setattr(signed_policy_metadata_gate, "ROOT", repo)
    monkeypatch.setattr(signed_policy_metadata_gate, "evidence_root", lambda: repo / "evidence")
    assert signed_policy_metadata_gate.main([]) == 0


def test_signed_policy_metadata_gate_fails_when_owner_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence" / "security"
    pol = repo / "governance" / "security"
    ev.mkdir(parents=True)
    pol.mkdir(parents=True)
    (pol / "policy_signature_manifest.json").write_text(
        json.dumps({"policies": ["governance/security/p1.json"]}) + "\n", encoding="utf-8"
    )
    (pol / "p1.json").write_text(json.dumps({"last_reviewed_utc": "2026-03-04T00:00:00+00:00"}) + "\n", encoding="utf-8")
    monkeypatch.setattr(signed_policy_metadata_gate, "ROOT", repo)
    monkeypatch.setattr(signed_policy_metadata_gate, "evidence_root", lambda: repo / "evidence")
    assert signed_policy_metadata_gate.main([]) == 1
    report = json.loads((ev / "signed_policy_metadata_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_owner:governance/security/p1.json" in report["findings"]
