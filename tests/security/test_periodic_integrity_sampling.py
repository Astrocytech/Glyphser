from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import periodic_integrity_sampling


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _sign(path: Path) -> None:
    sig = sign_file(path, key=current_key(strict=False))
    path.with_suffix(path.suffix + ".sig").write_text(sig + "\n", encoding="utf-8")


def _make_run(repo: Path, run_id: str, stage: str) -> None:
    sec = repo / "evidence" / "runs" / run_id / stage / "security"
    _write(sec / "security_super_gate.json", {"status": "PASS"})
    _write(sec / "evidence_attestation_index.json", {"status": "PASS"})
    _write(sec / "rolling_merkle_checkpoints.json", {"status": "PASS"})
    bundle = sec / "restored-evidence.tar.gz"
    bundle.write_text("restored-payload", encoding="utf-8")
    _write(
        sec / "long_term_retention_manifest.json",
        {
            "entries": [
                {
                    "path": str(bundle.relative_to(repo)).replace("\\", "/"),
                    "sha256": periodic_integrity_sampling._sha256(bundle),
                }
            ]
        },
    )
    _sign(sec / "evidence_attestation_index.json")
    _sign(sec / "rolling_merkle_checkpoints.json")
    _sign(sec / "long_term_retention_manifest.json")


def test_periodic_integrity_sampling_passes_with_signed_historical_runs(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _make_run(repo, "1001", "release-build")
    _make_run(repo, "1002", "release-build")

    monkeypatch.setattr(periodic_integrity_sampling, "ROOT", repo)
    monkeypatch.setattr(periodic_integrity_sampling, "RUNS_ROOT", repo / "evidence" / "runs")
    monkeypatch.setattr(periodic_integrity_sampling, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_INTEGRITY_SAMPLE_SIZE", "2")
    monkeypatch.setenv("GLYPHSER_INTEGRITY_SAMPLE_SEED", "unit-test-seed")
    assert periodic_integrity_sampling.main([]) == 0

    report = json.loads((repo / "evidence" / "security" / "periodic_integrity_sampling.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["sampled_run_count"] == 2


def test_periodic_integrity_sampling_fails_when_signatures_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "runs" / "2001" / "release-build" / "security"
    _write(sec / "security_super_gate.json", {"status": "PASS"})
    _write(sec / "evidence_attestation_index.json", {"status": "PASS"})
    _write(sec / "rolling_merkle_checkpoints.json", {"status": "PASS"})

    monkeypatch.setattr(periodic_integrity_sampling, "ROOT", repo)
    monkeypatch.setattr(periodic_integrity_sampling, "RUNS_ROOT", repo / "evidence" / "runs")
    monkeypatch.setattr(periodic_integrity_sampling, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_INTEGRITY_SAMPLE_SIZE", "1")
    monkeypatch.setenv("GLYPHSER_INTEGRITY_SAMPLE_SEED", "unit-test-seed")
    assert periodic_integrity_sampling.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "periodic_integrity_sampling.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("failed_sampled_runs:") for item in report["findings"])


def test_periodic_integrity_sampling_fails_when_restored_evidence_mismatches_manifest(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _make_run(repo, "3001", "release-build")
    bundle = repo / "evidence" / "runs" / "3001" / "release-build" / "security" / "restored-evidence.tar.gz"
    bundle.write_text("tampered-payload", encoding="utf-8")

    monkeypatch.setattr(periodic_integrity_sampling, "ROOT", repo)
    monkeypatch.setattr(periodic_integrity_sampling, "RUNS_ROOT", repo / "evidence" / "runs")
    monkeypatch.setattr(periodic_integrity_sampling, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_INTEGRITY_SAMPLE_SIZE", "1")
    monkeypatch.setenv("GLYPHSER_INTEGRITY_SAMPLE_SEED", "unit-test-seed")
    assert periodic_integrity_sampling.main([]) == 1

    report = json.loads((repo / "evidence" / "security" / "periodic_integrity_sampling.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    run_findings = report["audits"][0]["findings"]
    assert any("restored_evidence_digest_mismatch:" in str(item) for item in run_findings)
