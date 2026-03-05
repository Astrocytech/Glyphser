from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import quarterly_restore_simulation


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _make_run(repo: Path, run_id: str) -> None:
    sec = repo / "evidence" / "runs" / run_id / "release-build" / "security"
    bundle = sec / "restore.tar.gz"
    bundle.parent.mkdir(parents=True, exist_ok=True)
    bundle.write_text("bundle", encoding="utf-8")
    digest = quarterly_restore_simulation._sha256(bundle)
    manifest = sec / "long_term_retention_manifest.json"
    _write(
        manifest,
        {
            "entries": [
                {
                    "path": str(bundle.relative_to(repo)).replace("\\", "/"),
                    "sha256": digest,
                }
            ]
        },
    )
    sig = sign_file(manifest, key=current_key(strict=False))
    manifest.with_suffix(".json.sig").write_text(sig + "\n", encoding="utf-8")


def test_quarterly_restore_simulation_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _make_run(repo, "7001")
    _make_run(repo, "7002")

    monkeypatch.setattr(quarterly_restore_simulation, "ROOT", repo)
    monkeypatch.setattr(quarterly_restore_simulation, "RUNS_ROOT", repo / "evidence" / "runs")
    monkeypatch.setattr(quarterly_restore_simulation, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_QUARTERLY_RESTORE_SAMPLE_SIZE", "2")
    monkeypatch.setenv("GLYPHSER_QUARTERLY_RESTORE_SEED", "test-seed")

    assert quarterly_restore_simulation.main([]) == 0


def test_quarterly_restore_simulation_fails_on_digest_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _make_run(repo, "7003")
    (repo / "evidence" / "runs" / "7003" / "release-build" / "security" / "restore.tar.gz").write_text(
        "tampered",
        encoding="utf-8",
    )

    monkeypatch.setattr(quarterly_restore_simulation, "ROOT", repo)
    monkeypatch.setattr(quarterly_restore_simulation, "RUNS_ROOT", repo / "evidence" / "runs")
    monkeypatch.setattr(quarterly_restore_simulation, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_QUARTERLY_RESTORE_SAMPLE_SIZE", "1")
    monkeypatch.setenv("GLYPHSER_QUARTERLY_RESTORE_SEED", "test-seed")

    assert quarterly_restore_simulation.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "quarterly_restore_simulation.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("failed_restore_simulations:") for item in report["findings"])
