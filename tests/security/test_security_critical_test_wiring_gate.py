from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_critical_test_wiring_gate


def test_security_critical_test_wiring_gate_passes(monkeypatch, tmp_path: Path) -> None:
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
                "  pull_request:",
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - name: Security targeted regression suite",
                "        run: pytest -q tests/security",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_critical_test_wiring_gate, "ROOT", repo)
    monkeypatch.setattr(security_critical_test_wiring_gate, "CI_PATH", wf / "ci.yml")
    monkeypatch.setattr(security_critical_test_wiring_gate, "evidence_root", lambda: repo / "evidence")
    assert security_critical_test_wiring_gate.main([]) == 0


def test_security_critical_test_wiring_gate_fails_when_suite_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text("on:\n  push:\njobs:\n  test:\n    runs-on: ubuntu-latest\n", encoding="utf-8")
    monkeypatch.setattr(security_critical_test_wiring_gate, "ROOT", repo)
    monkeypatch.setattr(security_critical_test_wiring_gate, "CI_PATH", wf / "ci.yml")
    monkeypatch.setattr(security_critical_test_wiring_gate, "evidence_root", lambda: repo / "evidence")
    assert security_critical_test_wiring_gate.main([]) == 1
    report = json.loads((ev / "security_critical_test_wiring_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("missing_required_snippet:") for item in report["findings"])
