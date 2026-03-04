from __future__ import annotations

import json
from pathlib import Path

from tooling.security import container_provenance_gate


def test_container_provenance_gate_passes_with_skip(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "container_provenance_policy.json").write_text(
        json.dumps(
            {
                "required_when_container_artifacts_present": True,
                "container_digest_manifest": "distribution/container/image-digests.txt",
                "required_signature_files": ["distribution/container/image-digests.txt.sig"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(container_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(container_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert container_provenance_gate.main() == 0


def test_container_provenance_gate_fails_when_required_files_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "distribution" / "container").mkdir(parents=True)
    (repo / "distribution" / "container" / "image-digests.txt").write_text("img@sha256:abc\n", encoding="utf-8")
    (repo / "governance" / "security" / "container_provenance_policy.json").write_text(
        json.dumps(
            {
                "required_when_container_artifacts_present": True,
                "container_digest_manifest": "distribution/container/image-digests.txt",
                "required_signature_files": ["distribution/container/image-digests.txt.sig"],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(container_provenance_gate, "ROOT", repo)
    monkeypatch.setattr(container_provenance_gate, "evidence_root", lambda: repo / "evidence")
    assert container_provenance_gate.main() == 1
