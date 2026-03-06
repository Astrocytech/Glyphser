from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_step_execution_fingerprint


def test_security_step_execution_fingerprint_writes_hashes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    (workflows / "security-maintenance.yml").write_text(
        """
name: security-maintenance
env:
  GLOBAL_A: top
  GLYPHSER_RUN_CORRELATION_ID: 123456
jobs:
  security-maintenance:
    env:
      JOB_A: mid
    steps:
      - name: Step One
        run: echo hello
      - name: Step Two
        env:
          STEP_A: low
        run: |
          echo alpha
          echo beta
""".strip()
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_step_execution_fingerprint, "ROOT", repo)
    monkeypatch.setattr(security_step_execution_fingerprint, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_step_execution_fingerprint, "evidence_root", lambda: repo / "evidence")
    assert security_step_execution_fingerprint.main([]) == 0

    report = json.loads((repo / "evidence" / "security" / "security_step_execution_fingerprint.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["fingerprinted_steps"] == 2
    first = report["fingerprints"][0]
    assert len(first["command_hash_sha256"]) == 64
    assert len(first["env_profile_hash_sha256"]) == 64
    assert first["start_marker"].startswith("STEP_START:")
    assert first["end_marker"].startswith("STEP_END:")
    assert first["run_correlation_id"] == "123456"


def test_security_step_execution_fingerprint_fails_when_no_run_steps(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    workflows.mkdir(parents=True, exist_ok=True)
    (workflows / "security-maintenance.yml").write_text("name: security-maintenance\njobs:\n  only:\n    steps:\n      - uses: actions/checkout@v4\n", encoding="utf-8")

    monkeypatch.setattr(security_step_execution_fingerprint, "ROOT", repo)
    monkeypatch.setattr(security_step_execution_fingerprint, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_step_execution_fingerprint, "evidence_root", lambda: repo / "evidence")
    assert security_step_execution_fingerprint.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_step_execution_fingerprint.json").read_text(encoding="utf-8"))
    assert "no_security_workflow_run_steps_found" in report["findings"]
