from __future__ import annotations

import json
from pathlib import Path

from tooling.security import release_evidence_root_isolation_gate


def _write_release(repo: Path, env_lines: list[str]) -> None:
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "release.yml").write_text("\n".join(["jobs:"] + env_lines) + "\n", encoding="utf-8")


def test_release_evidence_root_isolation_gate_passes_for_release_scoped_roots(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_release(
        repo,
        [
            '  build:\n    env:\n      GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/release-build',
            '  verify:\n    env:\n      GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/release-verify',
            '  publish:\n    env:\n      GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/release-publish',
        ],
    )
    monkeypatch.setattr(release_evidence_root_isolation_gate, "ROOT", repo)
    monkeypatch.setattr(
        release_evidence_root_isolation_gate, "RELEASE_WORKFLOW", repo / ".github" / "workflows" / "release.yml"
    )
    monkeypatch.setattr(release_evidence_root_isolation_gate, "evidence_root", lambda: repo / "evidence")
    assert release_evidence_root_isolation_gate.main([]) == 0


def test_release_evidence_root_isolation_gate_fails_for_ci_or_maintenance_roots(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_release(
        repo,
        [
            '  build:\n    env:\n      GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/release-build',
            '  verify:\n    env:\n      GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-maintenance',
        ],
    )
    monkeypatch.setattr(release_evidence_root_isolation_gate, "ROOT", repo)
    monkeypatch.setattr(
        release_evidence_root_isolation_gate, "RELEASE_WORKFLOW", repo / ".github" / "workflows" / "release.yml"
    )
    monkeypatch.setattr(release_evidence_root_isolation_gate, "evidence_root", lambda: repo / "evidence")
    assert release_evidence_root_isolation_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "release_evidence_root_isolation_gate.json").read_text(encoding="utf-8")
    )
    assert any(item.startswith("non_release_evidence_root:") for item in report["findings"])
    assert any(item.startswith("release_evidence_root_not_isolated:") for item in report["findings"])
