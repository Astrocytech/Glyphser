from __future__ import annotations

import json
from pathlib import Path

from tooling.security import workflow_pinning_gate


def test_workflow_pinning_gate_passes_for_sha_pins(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "jobs:\n  test:\n    steps:\n      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683\n",
        encoding="utf-8",
    )

    out_root = tmp_path / "evidence"
    monkeypatch.setattr(workflow_pinning_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_pinning_gate, "evidence_root", lambda: out_root)

    rc = workflow_pinning_gate.main()
    assert rc == 0
    report = json.loads((out_root / "security" / "workflow_pinning.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["finding_count"] == 0


def test_workflow_pinning_gate_fails_for_tag_refs(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True)
    (wf / "ci.yml").write_text(
        "jobs:\n  test:\n    steps:\n      - uses: actions/checkout@v4\n",
        encoding="utf-8",
    )

    out_root = tmp_path / "evidence"
    monkeypatch.setattr(workflow_pinning_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_pinning_gate, "evidence_root", lambda: out_root)

    rc = workflow_pinning_gate.main()
    assert rc == 1
    report = json.loads((out_root / "security" / "workflow_pinning.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert report["finding_count"] == 1


def test_workflow_pinning_gate_allows_active_exception(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    sec = repo / "governance" / "security"
    wf.mkdir(parents=True)
    sec.mkdir(parents=True)
    uses_ref = "actions/checkout@v4"
    (wf / "ci.yml").write_text(
        f"jobs:\n  test:\n    steps:\n      - uses: {uses_ref}\n",
        encoding="utf-8",
    )
    (sec / "workflow_pinning_exceptions.json").write_text(
        json.dumps(
            {
                "exceptions": [
                    {
                        "workflow": ".github/workflows/ci.yml",
                        "uses": uses_ref,
                        "expires_at_utc": "2099-01-01T00:00:00+00:00",
                        "reason": "temporary vendor lag",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    out_root = tmp_path / "evidence"
    monkeypatch.setattr(workflow_pinning_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_pinning_gate, "EXCEPTIONS_PATH", sec / "workflow_pinning_exceptions.json")
    monkeypatch.setattr(workflow_pinning_gate, "evidence_root", lambda: out_root)

    rc = workflow_pinning_gate.main()
    assert rc == 0
    report = json.loads((out_root / "security" / "workflow_pinning.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["finding_count"] == 0
    assert len(report["suppressed_findings"]) == 1


def test_workflow_pinning_gate_fails_on_expired_exception(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    sec = repo / "governance" / "security"
    wf.mkdir(parents=True)
    sec.mkdir(parents=True)
    uses_ref = "actions/setup-python@v5"
    (wf / "ci.yml").write_text(
        f"jobs:\n  test:\n    steps:\n      - uses: {uses_ref}\n",
        encoding="utf-8",
    )
    (sec / "workflow_pinning_exceptions.json").write_text(
        json.dumps(
            {
                "exceptions": [
                    {
                        "workflow": ".github/workflows/ci.yml",
                        "uses": uses_ref,
                        "expires_at_utc": "2000-01-01T00:00:00+00:00",
                        "reason": "expired exception",
                    }
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )

    out_root = tmp_path / "evidence"
    monkeypatch.setattr(workflow_pinning_gate, "ROOT", repo)
    monkeypatch.setattr(workflow_pinning_gate, "EXCEPTIONS_PATH", sec / "workflow_pinning_exceptions.json")
    monkeypatch.setattr(workflow_pinning_gate, "evidence_root", lambda: out_root)

    rc = workflow_pinning_gate.main()
    assert rc == 1
    report = json.loads((out_root / "security" / "workflow_pinning.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert report["policy_finding_count"] >= 1
    assert any(str(item).startswith("workflow_pinning_exception_expired:") for item in report["policy_findings"])
