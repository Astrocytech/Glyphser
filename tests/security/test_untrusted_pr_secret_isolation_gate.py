from __future__ import annotations

import json
from pathlib import Path

from tooling.security import untrusted_pr_secret_isolation_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_untrusted_pr_secret_isolation_gate_passes_with_fork_guard(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    (repo / "evidence" / "security").mkdir(parents=True)
    _write(
        wf / "security-maintenance.yml",
        (
            "on:\n  pull_request:\njobs:\n  test:\n    if: github.event.pull_request.head.repo.fork == false\n"
            "    steps:\n      - run: echo ${{ secrets.GLYPHSER_PROVENANCE_HMAC_KEY }}\n"
        ),
    )
    monkeypatch.setattr(untrusted_pr_secret_isolation_gate, "ROOT", repo)
    monkeypatch.setattr(untrusted_pr_secret_isolation_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(untrusted_pr_secret_isolation_gate, "evidence_root", lambda: repo / "evidence")
    assert untrusted_pr_secret_isolation_gate.main([]) == 0


def test_untrusted_pr_secret_isolation_gate_fails_on_unguarded_secret_usage(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    sec = repo / "evidence" / "security"
    sec.mkdir(parents=True)
    _write(
        wf / "security-maintenance.yml",
        (
            "on:\n  pull_request:\njobs:\n  test:\n"
            "    steps:\n      - run: echo ${{ secrets.GLYPHSER_PROVENANCE_HMAC_KEY }}\n"
        ),
    )
    monkeypatch.setattr(untrusted_pr_secret_isolation_gate, "ROOT", repo)
    monkeypatch.setattr(untrusted_pr_secret_isolation_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(untrusted_pr_secret_isolation_gate, "evidence_root", lambda: repo / "evidence")
    assert untrusted_pr_secret_isolation_gate.main([]) == 1
    report = json.loads((sec / "untrusted_pr_secret_isolation_gate.json").read_text(encoding="utf-8"))
    assert "unguarded_secret_usage_in_pull_request_workflow:.github/workflows/security-maintenance.yml" in report["findings"]
