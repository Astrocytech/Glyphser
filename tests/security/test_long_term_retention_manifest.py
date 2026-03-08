from __future__ import annotations

import json
from pathlib import Path

from tooling.security import long_term_retention_manifest


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_long_term_retention_manifest_passes_with_valid_bundle_digest(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "security_retention_policy.json"
    _write(
        policy,
        json.dumps(
            {
                "storage_location": "immutable://glyphser-security-evidence",
                "retention_class": "long_term",
                "legal_hold_supported": True,
                "manifest_required": True,
            }
        )
        + "\n",
    )
    bundle = repo / "evidence" / "incident" / "incident-bundle-1.tar.gz"
    _write(bundle, "bundle-data")
    digest = long_term_retention_manifest._sha256(bundle)
    _write(bundle.with_name(bundle.name + ".sha256"), f"{digest}  {bundle.name}\n")

    monkeypatch.setattr(long_term_retention_manifest, "ROOT", repo)
    monkeypatch.setattr(long_term_retention_manifest, "POLICY", policy)
    monkeypatch.setattr(long_term_retention_manifest, "evidence_root", lambda: repo / "evidence")

    assert long_term_retention_manifest.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "long_term_retention_manifest.json").read_text("utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["bundle_count"] == 1
    assert report["summary"]["immutable_manifest_digest"].startswith("sha256:")


def test_long_term_retention_manifest_fails_on_missing_digest_sidecar(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "security_retention_policy.json"
    _write(
        policy,
        json.dumps(
            {
                "storage_location": "immutable://glyphser-security-evidence",
                "retention_class": "long_term",
                "legal_hold_supported": True,
                "manifest_required": True,
            }
        )
        + "\n",
    )
    _write(repo / "evidence" / "security" / "audit-log-archive.tar.gz", "archive")

    monkeypatch.setattr(long_term_retention_manifest, "ROOT", repo)
    monkeypatch.setattr(long_term_retention_manifest, "POLICY", policy)
    monkeypatch.setattr(long_term_retention_manifest, "evidence_root", lambda: repo / "evidence")

    assert long_term_retention_manifest.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "long_term_retention_manifest.json").read_text("utf-8"))
    assert any(str(item).startswith("missing_bundle_digest:") for item in report["findings"])
