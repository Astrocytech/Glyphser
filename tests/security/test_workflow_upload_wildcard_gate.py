from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_upload_wildcard_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_workflow_upload_wildcard_gate_passes_without_wildcards(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    body = (
        "jobs:\n"
        "  security:\n"
        "    steps:\n"
        "      - name: Upload security artifacts\n"
        "        uses: actions/upload-artifact@x\n"
        "        with:\n"
        "          path: |\n"
        "            evidence/security/report.json\n"
        "            evidence/security/report.json.sig\n"
    )
    _write(repo / ".github" / "workflows" / "ci.yml", body)
    _write(repo / ".github" / "workflows" / "security-maintenance.yml", body)
    _write(repo / ".github" / "workflows" / "security-super-extended.yml", body)

    monkeypatch.setattr(workflow_upload_wildcard_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_upload_wildcard_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_upload_wildcard_gate.main([]) == 0


def test_workflow_upload_wildcard_gate_fails_on_wildcard_path(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(
        repo / ".github" / "workflows" / "ci.yml",
        "jobs:\n  security:\n    steps:\n      - name: Upload security artifacts\n"
        "        uses: actions/upload-artifact@x\n"
        "        with:\n"
        "          path: |\n"
        "            evidence/security/*.json\n",
    )
    _write(repo / ".github" / "workflows" / "security-maintenance.yml", "jobs:\n  security-maintenance:\n    steps:\n")
    _write(repo / ".github" / "workflows" / "security-super-extended.yml", "jobs:\n  security-super-extended:\n    steps:\n")

    monkeypatch.setattr(workflow_upload_wildcard_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_upload_wildcard_gate, "evidence_root", lambda: repo / "evidence")
    assert workflow_upload_wildcard_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_upload_wildcard_gate.json").read_text(encoding="utf-8"))
    assert any(str(item).startswith("wildcard_upload_path:.github/workflows/ci.yml:Upload security artifacts:") for item in report["findings"])
