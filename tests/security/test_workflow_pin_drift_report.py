from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_pin_drift_report


def test_workflow_pin_drift_report_writes_signed_report(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text("jobs:\n  x:\n    steps:\n      - uses: actions/checkout@v4\n", encoding="utf-8")

    class _Signing:
        @staticmethod
        def current_key(strict: bool = False) -> str:
            return "k"

        @staticmethod
        def sign_file(path: Path, key: str) -> str:
            _ = path, key
            return "sig"

    monkeypatch.setattr(workflow_pin_drift_report, "ROOT", repo)
    monkeypatch.setattr(workflow_pin_drift_report, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(workflow_pin_drift_report, "artifact_signing", _Signing)
    assert workflow_pin_drift_report.main([]) == 0
    report = json.loads((ev / "workflow_pin_drift_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["unpinned_references"] == 1
    assert (ev / "workflow_pin_drift_report.json.sig").read_text(encoding="utf-8").strip() == "sig"
