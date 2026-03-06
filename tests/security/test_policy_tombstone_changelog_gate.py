from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import bootstrap_key, sign_file
from tooling.security import policy_tombstone_changelog_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    path.with_suffix(".json.sig").write_text(sign_file(path, key=bootstrap_key()) + "\n", encoding="utf-8")


def test_policy_tombstone_changelog_gate_passes_with_signed_changelog(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "governance" / "security"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)

    _write_json(sec / "policy_signature_manifest.json", {"policies": ["governance/security/a.json"]})
    _write_json(sec / "a.json", {"owner": "sec", "last_reviewed_utc": "2026-03-01T00:00:00+00:00"})
    _write_json(sec / "policy_deprecation_registry.json", {"deprecations": []})
    _write_json(sec / "policy_tombstone_changelog.json", {"schema_version": "glyphser-policy-tombstones.v1", "tombstones": []})
    _sign(sec / "policy_tombstone_changelog.json")

    monkeypatch.setattr(policy_tombstone_changelog_gate, "ROOT", repo)
    monkeypatch.setattr(policy_tombstone_changelog_gate, "MANIFEST", sec / "policy_signature_manifest.json")
    monkeypatch.setattr(policy_tombstone_changelog_gate, "REGISTRY", sec / "policy_deprecation_registry.json")
    monkeypatch.setattr(policy_tombstone_changelog_gate, "TOMBSTONES", sec / "policy_tombstone_changelog.json")
    monkeypatch.setattr(policy_tombstone_changelog_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_tombstone_changelog_gate.main([]) == 0


def test_policy_tombstone_changelog_gate_fails_missing_tombstone_for_removed_policy(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "governance" / "security"
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True, exist_ok=True)

    _write_json(sec / "policy_signature_manifest.json", {"policies": []})
    _write_json(
        sec / "policy_deprecation_registry.json",
        {"deprecations": [{"policy": "governance/security/removed.json", "sunset_date_utc": "2026-01-01T00:00:00+00:00"}]},
    )
    _write_json(sec / "policy_tombstone_changelog.json", {"schema_version": "glyphser-policy-tombstones.v1", "tombstones": []})
    _sign(sec / "policy_tombstone_changelog.json")

    monkeypatch.setattr(policy_tombstone_changelog_gate, "ROOT", repo)
    monkeypatch.setattr(policy_tombstone_changelog_gate, "MANIFEST", sec / "policy_signature_manifest.json")
    monkeypatch.setattr(policy_tombstone_changelog_gate, "REGISTRY", sec / "policy_deprecation_registry.json")
    monkeypatch.setattr(policy_tombstone_changelog_gate, "TOMBSTONES", sec / "policy_tombstone_changelog.json")
    monkeypatch.setattr(policy_tombstone_changelog_gate, "evidence_root", lambda: repo / "evidence")
    assert policy_tombstone_changelog_gate.main([]) == 1
    report = json.loads((ev / "policy_tombstone_changelog_gate.json").read_text(encoding="utf-8"))
    assert "missing_tombstone_for_removed_policy:governance/security/removed.json" in report["findings"]
