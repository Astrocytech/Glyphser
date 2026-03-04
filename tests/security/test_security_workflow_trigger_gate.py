from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_workflow_trigger_gate


def test_security_workflow_trigger_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)

    (wf / "ci.yml").write_text(
        "\n".join(
            [
                "on:",
                "  push:",
                "    branches: [main]",
                "  pull_request:",
                "jobs:",
                "  security-matrix:",
                "    strategy:",
                "      matrix:",
                '        python-version: ["3.11", "3.12"]',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (wf / "security-super-extended.yml").write_text(
        "\n".join(
            [
                "on:",
                "  schedule:",
                "    - cron: '0 0 * * 0'",
                "  workflow_dispatch:",
                "jobs:",
                "  security-super-extended:",
                "    runs-on: ubuntu-latest",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(security_workflow_trigger_gate, "ROOT", repo)
    monkeypatch.setattr(security_workflow_trigger_gate, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_trigger_gate.main([]) == 0


def test_security_workflow_trigger_gate_fails_when_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)

    (wf / "ci.yml").write_text("on:\n  push:\njobs:\n  test:\n    runs-on: ubuntu-latest\n", encoding="utf-8")

    monkeypatch.setattr(security_workflow_trigger_gate, "ROOT", repo)
    monkeypatch.setattr(security_workflow_trigger_gate, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_trigger_gate.main([]) == 1
    report = json.loads((ev / "security_workflow_trigger_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("missing_") for item in report["findings"])
