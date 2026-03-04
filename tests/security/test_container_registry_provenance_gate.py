from __future__ import annotations

import json
from pathlib import Path

from tooling.security import container_registry_provenance_gate


def _write_policy(repo: Path, *, publishing_enabled: bool) -> None:
    policy = repo / "governance" / "security" / "container_provenance_policy.json"
    policy.parent.mkdir(parents=True, exist_ok=True)
    policy.write_text(
        json.dumps(
            {
                "container_publishing_enabled": publishing_enabled,
                "container_digest_manifest": "distribution/container/image-digests.txt",
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_container_registry_provenance_gate_skips_when_publish_disabled(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo, publishing_enabled=False)
    monkeypatch.setattr(container_registry_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(
        container_registry_provenance_gate,
        "POLICY",
        repo / "governance" / "security" / "container_provenance_policy.json",
    )
    monkeypatch.setattr(container_registry_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert container_registry_provenance_gate.main([]) == 0


def test_container_registry_provenance_gate_fails_without_verification_report(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo, publishing_enabled=True)
    digest = "sha256:" + "a" * 64
    manifest = repo / "distribution" / "container" / "image-digests.txt"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"img@{digest}\n", encoding="utf-8")
    monkeypatch.setattr(container_registry_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(
        container_registry_provenance_gate,
        "POLICY",
        repo / "governance" / "security" / "container_provenance_policy.json",
    )
    monkeypatch.setattr(container_registry_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert container_registry_provenance_gate.main([]) == 1


def test_container_registry_provenance_gate_passes_with_matching_verification_report(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_policy(repo, publishing_enabled=True)
    digest = "sha256:" + "b" * 64
    manifest = repo / "distribution" / "container" / "image-digests.txt"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(f"img@{digest}\n", encoding="utf-8")
    verify_report = repo / "distribution" / "container" / "registry-provenance-verify.json"
    verify_report.write_text(
        json.dumps({"status": "PASS", "verified_digests": [digest]}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(container_registry_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(
        container_registry_provenance_gate,
        "POLICY",
        repo / "governance" / "security" / "container_provenance_policy.json",
    )
    monkeypatch.setattr(container_registry_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert container_registry_provenance_gate.main([]) == 0
