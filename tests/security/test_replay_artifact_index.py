from __future__ import annotations

import json
from pathlib import Path

from tooling.security import replay_artifact_index


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _seed_required_reports(run_dir: Path) -> None:
    sec = run_dir / "security"
    for name in replay_artifact_index.REQUIRED_SECURITY_REPORTS:
        _write(sec / name, '{"status":"PASS"}\n')


def test_replay_artifact_index_passes_when_replay_bundle_is_complete(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "evidence" / "runs" / "301" / "security-maintenance"
    _seed_required_reports(run_dir)
    bundle = run_dir / "incident" / "incident-bundle-301.tar.gz"
    _write(bundle, "bundle-bytes")
    _write(bundle.with_suffix(bundle.suffix + ".sha256"), "deadbeef")
    _write(bundle.with_suffix(bundle.suffix + ".manifest.json"), '{"files":[]}\n')

    monkeypatch.setattr(replay_artifact_index, "ROOT", repo)
    monkeypatch.setattr(replay_artifact_index, "evidence_root", lambda: repo / "evidence")
    assert replay_artifact_index.main(["--run-dir", str(run_dir)]) == 0
    report = json.loads((repo / "evidence" / "security" / "replay_artifact_index.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["indexed_artifacts"] >= len(replay_artifact_index.REQUIRED_SECURITY_REPORTS)


def test_replay_artifact_index_fails_when_required_replay_artifacts_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    run_dir = repo / "evidence" / "runs" / "302" / "security-maintenance"
    _seed_required_reports(run_dir)
    # Intentionally omit one required report and all incident artifacts.
    (run_dir / "security" / "deterministic_replay_harness.json").unlink()

    monkeypatch.setattr(replay_artifact_index, "ROOT", repo)
    monkeypatch.setattr(replay_artifact_index, "evidence_root", lambda: repo / "evidence")
    assert replay_artifact_index.main(["--run-dir", str(run_dir)]) == 1
    report = json.loads((repo / "evidence" / "security" / "replay_artifact_index.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert "missing_replay_artifact:deterministic_replay_harness.json" in report["findings"]
    assert "missing_incident_bundle_tarball" in report["findings"]
