from __future__ import annotations

import json
from pathlib import Path

from tooling.security import cosign_attestation_gate


def test_cosign_attestation_gate_skips_when_not_applicable(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "distribution" / "container").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    monkeypatch.setattr(cosign_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(cosign_attestation_gate, "evidence_root", lambda: repo / "evidence")
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "container_provenance_policy.json").write_text(
        json.dumps(
            {
                "required_when_container_artifacts_present": True,
                "container_publishing_enabled": False,
                "cosign_required_lanes": ["release"],
                "cosign_skippable_lanes": ["ci"],
                "required_signature_files": [
                    "distribution/container/image-digests.txt.sig",
                    "distribution/container/slsa-provenance.intoto.jsonl",
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("GLYPHSER_CONTAINER_PUBLISHING_ENABLED", raising=False)
    monkeypatch.setenv("GLYPHSER_SECURITY_LANE", "ci")

    assert cosign_attestation_gate.main([]) == 0
    out = json.loads((repo / "evidence" / "security" / "cosign_attestation_gate.json").read_text(encoding="utf-8"))
    assert out["status"] == "PASS"
    assert out["skipped"] is True


def test_cosign_attestation_gate_fails_when_publishing_enabled_without_attestations(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    (repo / "distribution" / "container").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    monkeypatch.setattr(cosign_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(cosign_attestation_gate, "evidence_root", lambda: repo / "evidence")
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "container_provenance_policy.json").write_text(
        json.dumps(
            {
                "required_when_container_artifacts_present": True,
                "container_publishing_enabled": False,
                "cosign_required_lanes": ["release"],
                "cosign_skippable_lanes": ["ci"],
                "required_signature_files": [
                    "distribution/container/image-digests.txt.sig",
                    "distribution/container/slsa-provenance.intoto.jsonl",
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("GLYPHSER_CONTAINER_PUBLISHING_ENABLED", "true")
    monkeypatch.setenv("GLYPHSER_SECURITY_LANE", "release")

    assert cosign_attestation_gate.main([]) == 1
    out = json.loads((repo / "evidence" / "security" / "cosign_attestation_gate.json").read_text(encoding="utf-8"))
    assert out["status"] == "FAIL"
    assert out["skipped"] is False


def test_cosign_attestation_gate_fails_on_required_lane_without_attestations(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "distribution" / "container").mkdir(parents=True)
    (repo / "evidence" / "security").mkdir(parents=True)
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "governance" / "security" / "container_provenance_policy.json").write_text(
        json.dumps(
            {
                "required_when_container_artifacts_present": False,
                "container_publishing_enabled": False,
                "cosign_required_lanes": ["release"],
                "cosign_skippable_lanes": ["ci"],
                "required_signature_files": [
                    "distribution/container/image-digests.txt.sig",
                    "distribution/container/slsa-provenance.intoto.jsonl",
                ],
            }
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(cosign_attestation_gate, "ROOT", repo)
    monkeypatch.setattr(cosign_attestation_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_SECURITY_LANE", "release")
    monkeypatch.delenv("GLYPHSER_CONTAINER_PUBLISHING_ENABLED", raising=False)

    assert cosign_attestation_gate.main([]) == 1
