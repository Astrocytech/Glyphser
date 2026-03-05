from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_workflow_wrapper


def test_security_workflow_wrapper_fails_when_required_env_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(security_workflow_wrapper, "ROOT", repo)
    monkeypatch.setattr(security_workflow_wrapper, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LC_ALL", "C.UTF-8")
    monkeypatch.setenv("LANG", "C.UTF-8")
    monkeypatch.delenv("GLYPHSER_EVIDENCE_ROOT", raising=False)
    monkeypatch.setattr(security_workflow_wrapper.shutil, "which", lambda _name: "/usr/bin/tool")
    assert security_workflow_wrapper.main(["--workflow", "ci"]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_workflow_wrapper_ci.json").read_text(encoding="utf-8"))
    assert "missing_env:GLYPHSER_EVIDENCE_ROOT" in report["findings"]


def test_security_workflow_wrapper_runs_wrapped_command_after_validation(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(security_workflow_wrapper, "ROOT", repo)
    monkeypatch.setattr(security_workflow_wrapper, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_EVIDENCE_ROOT", "evidence/runs/1/ci")
    monkeypatch.setenv("TZ", "UTC")
    monkeypatch.setenv("LC_ALL", "C.UTF-8")
    monkeypatch.setenv("LANG", "C.UTF-8")
    monkeypatch.setattr(security_workflow_wrapper.shutil, "which", lambda _name: "/usr/bin/tool")

    class _Proc:
        returncode = 0
        stdout = "ok"
        stderr = ""

    monkeypatch.setattr(security_workflow_wrapper, "run_checked", lambda *args, **kwargs: _Proc())
    assert security_workflow_wrapper.main(["--workflow", "ci", "--", "echo", "ok"]) == 0
    report = json.loads((repo / "evidence" / "security" / "security_workflow_wrapper_ci.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["metadata"]["command_result"]["ran"] is True
