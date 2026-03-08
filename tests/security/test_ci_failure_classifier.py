from __future__ import annotations

import json
from pathlib import Path

from tooling.security import ci_failure_classifier


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_ci_failure_classifier_marks_recurring_issues(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    sec = ev / "security"

    _write_json(sec / "gate_a.json", {"status": "FAIL", "findings": ["timeout"], "summary": {}, "metadata": {}})
    _write_json(sec / "gate_b.json", {"status": "WARN", "findings": ["flaky"], "summary": {}, "metadata": {}})
    _write_json(
        repo / "evidence" / "security" / "ci_failure_classifier_history.json",
        {
            "schema_version": 1,
            "counts": {"gate_a.json:timeout": 1, "other_gate.json:old_issue": 2},
            "runs": [],
        },
    )

    monkeypatch.setattr(ci_failure_classifier, "ROOT", repo)
    monkeypatch.setattr(ci_failure_classifier, "PERSISTENT_HISTORY", repo / "evidence" / "security" / "ci_failure_classifier_history.json")
    monkeypatch.setattr(ci_failure_classifier, "evidence_root", lambda: ev)

    assert ci_failure_classifier.main([]) == 0

    report = json.loads((sec / "ci_failure_classifier.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert "gate_a.json:timeout" in report["classification"]["recurring_issues"]
    assert "gate_b.json:flaky" in report["classification"]["new_issues"]

    history = json.loads((sec / "ci_failure_classifier_history.json").read_text(encoding="utf-8"))
    assert history["counts"]["gate_a.json:timeout"] == 2
    assert history["counts"]["gate_b.json:flaky"] == 1


def test_ci_failure_classifier_passes_without_failures(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    sec = ev / "security"

    _write_json(sec / "gate_pass.json", {"status": "PASS", "findings": [], "summary": {}, "metadata": {}})

    monkeypatch.setattr(ci_failure_classifier, "ROOT", repo)
    monkeypatch.setattr(ci_failure_classifier, "PERSISTENT_HISTORY", repo / "evidence" / "security" / "ci_failure_classifier_history.json")
    monkeypatch.setattr(ci_failure_classifier, "evidence_root", lambda: ev)

    assert ci_failure_classifier.main([]) == 0
    report = json.loads((sec / "ci_failure_classifier.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["current_issue_count"] == 0


def test_ci_failure_classifier_reports_invalid_json_inputs(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    ev = repo / "evidence"
    sec = ev / "security"
    sec.mkdir(parents=True, exist_ok=True)
    (sec / "bad.json").write_text("{not-json}\n", encoding="utf-8")

    monkeypatch.setattr(ci_failure_classifier, "ROOT", repo)
    monkeypatch.setattr(ci_failure_classifier, "PERSISTENT_HISTORY", repo / "evidence" / "security" / "ci_failure_classifier_history.json")
    monkeypatch.setattr(ci_failure_classifier, "evidence_root", lambda: ev)

    assert ci_failure_classifier.main([]) == 0
    report = json.loads((sec / "ci_failure_classifier.json").read_text(encoding="utf-8"))
    assert report["status"] == "WARN"
    assert "invalid_security_report_json:bad.json" in report["findings"]
