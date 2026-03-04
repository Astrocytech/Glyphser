from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_sarif_permissions_gate


def test_security_sarif_permissions_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    ev = repo / "evidence" / "security"
    wf.mkdir(parents=True)
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "\n".join(
            [
                "permissions:",
                "  contents: read",
                "  security-events: write",
                "jobs:",
                "  sec:",
                "    steps:",
                "      - if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.fork == false",
                "        uses: github/codeql-action/upload-sarif@abc",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(security_sarif_permissions_gate, "ROOT", repo)
    monkeypatch.setattr(security_sarif_permissions_gate, "evidence_root", lambda: repo / "evidence")
    assert security_sarif_permissions_gate.main([]) == 0


def test_security_sarif_permissions_gate_fails_when_missing_controls(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    ev = repo / "evidence" / "security"
    wf.mkdir(parents=True)
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "\n".join(
            [
                "jobs:",
                "  sec:",
                "    steps:",
                "      - uses: github/codeql-action/upload-sarif@abc",
            ]
        ),
        encoding="utf-8",
    )

    monkeypatch.setattr(security_sarif_permissions_gate, "ROOT", repo)
    monkeypatch.setattr(security_sarif_permissions_gate, "evidence_root", lambda: repo / "evidence")
    assert security_sarif_permissions_gate.main([]) == 1
    report = json.loads((ev / "security_sarif_permissions_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("missing_fork_guard:") for item in report["findings"])
    assert any(item.startswith("missing_security_events_permission:") for item in report["findings"])
