from __future__ import annotations

import json
from pathlib import Path

from tooling.security import promotion_go_no_go_report


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_promotion_go_no_go_report_passes_when_weighted_controls_and_blockers_clear(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "promotion_go_no_go_policy.json"
    _write(
        policy,
        {
            "minimum_weighted_score": 80,
            "controls": [
                {
                    "name": "super",
                    "report_path": "evidence/security/security_super_gate.json",
                    "weight": 70,
                    "mandatory": True,
                },
                {
                    "name": "summary",
                    "report_path": "evidence/security/security_verification_summary.json",
                    "weight": 30,
                    "mandatory": False,
                },
            ],
        },
    )
    _write(repo / "evidence" / "security" / "security_super_gate.json", {"status": "PASS"})
    _write(repo / "evidence" / "security" / "security_verification_summary.json", {"status": "PASS"})

    monkeypatch.setattr(promotion_go_no_go_report, "ROOT", repo)
    monkeypatch.setattr(promotion_go_no_go_report, "POLICY", policy)
    monkeypatch.setattr(promotion_go_no_go_report, "evidence_root", lambda: repo / "evidence")

    assert promotion_go_no_go_report.main([]) == 0
    report = json.loads((repo / "evidence" / "security" / "promotion_go_no_go_report.json").read_text(encoding="utf-8"))
    assert report["summary"]["promotion_blocker_count"] == 0
    assert report["summary"]["promotion_blockers"] == []


def test_promotion_go_no_go_report_fails_when_mandatory_control_not_pass(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "promotion_go_no_go_policy.json"
    _write(
        policy,
        {
            "minimum_weighted_score": 80,
            "controls": [
                {
                    "name": "super",
                    "report_path": "evidence/security/security_super_gate.json",
                    "weight": 100,
                    "mandatory": True,
                }
            ],
        },
    )
    _write(repo / "evidence" / "security" / "security_super_gate.json", {"status": "WARN"})

    monkeypatch.setattr(promotion_go_no_go_report, "ROOT", repo)
    monkeypatch.setattr(promotion_go_no_go_report, "POLICY", policy)
    monkeypatch.setattr(promotion_go_no_go_report, "evidence_root", lambda: repo / "evidence")

    assert promotion_go_no_go_report.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "promotion_go_no_go_report.json").read_text(encoding="utf-8"))
    assert report["summary"]["decision"] == "NO_GO"
    assert any(str(item).startswith("mandatory_control_not_pass:super:WARN") for item in report["findings"])
    assert report["summary"]["promotion_blocker_count"] >= 1
    assert any(item.get("class") == "mandatory_control_not_pass" for item in report["summary"]["promotion_blockers"])


def test_promotion_go_no_go_report_fails_when_warn_threshold_exceeded(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "promotion_go_no_go_policy.json"
    _write(
        policy,
        {
            "minimum_weighted_score": 0,
            "warn_thresholds_by_env": {"prod": {"advisory": 0}},
            "controls": [
                {
                    "name": "summary",
                    "report_path": "evidence/security/security_verification_summary.json",
                    "weight": 100,
                    "mandatory": False,
                }
            ],
        },
    )
    _write(
        repo / "evidence" / "security" / "security_verification_summary.json",
        {"status": "PASS", "warning_categories": {"advisory": 1}},
    )

    monkeypatch.setattr(promotion_go_no_go_report, "ROOT", repo)
    monkeypatch.setattr(promotion_go_no_go_report, "POLICY", policy)
    monkeypatch.setattr(promotion_go_no_go_report, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_DEPLOY_ENV", "prod")

    assert promotion_go_no_go_report.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "promotion_go_no_go_report.json").read_text(encoding="utf-8"))
    assert report["summary"]["decision"] == "NO_GO"
    assert any(str(item).startswith("warn_threshold_exceeded:prod:advisory:1:0") for item in report["findings"])
    assert any(item.get("class") == "warn_threshold_exceeded" for item in report["summary"]["promotion_blockers"])


def test_promotion_go_no_go_report_fails_when_warn_is_present_in_release_lane(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "promotion_go_no_go_policy.json"
    _write(
        policy,
        {
            "minimum_weighted_score": 0,
            "controls": [
                {
                    "name": "summary",
                    "report_path": "evidence/security/security_verification_summary.json",
                    "weight": 100,
                    "mandatory": False,
                }
            ],
        },
    )
    _write(repo / "evidence" / "security" / "security_verification_summary.json", {"status": "WARN"})

    monkeypatch.setattr(promotion_go_no_go_report, "ROOT", repo)
    monkeypatch.setattr(promotion_go_no_go_report, "POLICY", policy)
    monkeypatch.setattr(promotion_go_no_go_report, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_DEPLOY_ENV", "release")

    assert promotion_go_no_go_report.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "promotion_go_no_go_report.json").read_text(encoding="utf-8"))
    assert report["summary"]["decision"] == "NO_GO"
    assert "release_warn_not_allowed:summary" in report["findings"]
    assert any(item.get("class") == "release_warn_not_allowed" for item in report["summary"]["promotion_blockers"])
