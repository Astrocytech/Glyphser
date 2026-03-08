from __future__ import annotations

import json
from pathlib import Path

from tooling.security import dependency_freshness_gate


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_dependency_freshness_gate_passes_for_fresh_transitive_vuln(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "requirements.lock").write_text("directpkg==1.0.0\n", encoding="utf-8")
    _write_json(
        repo / "governance" / "security" / "dependency_freshness_policy.json",
        {
            "max_known_vulnerable_age_days": 14,
            "enforce_transitive_only": True,
            "fail_on_missing_pip_audit_report": True,
            "history_path": "evidence/security/dependency_vulnerability_freshness_history.json",
        },
    )
    _write_json(
        sec / "pip_audit.json",
        {
            "metadata": {"generated_at_utc": "2026-03-05T00:00:00+00:00"},
            "report": [
                {"name": "directpkg", "vulns": [{"id": "GHSA-direct"}]},
                {"name": "transitivepkg", "vulns": [{"id": "GHSA-fresh"}]},
            ],
        },
    )
    _write_json(
        sec / "dependency_vulnerability_freshness_history.json",
        {
            "entries": {
                "transitivepkg|GHSA-fresh": {
                    "package": "transitivepkg",
                    "vulnerability_id": "GHSA-fresh",
                    "first_seen_utc": "2026-03-01T00:00:00+00:00",
                    "last_seen_utc": "2026-03-01T00:00:00+00:00",
                    "resolved_at_utc": "",
                }
            }
        },
    )

    monkeypatch.setattr(dependency_freshness_gate, "ROOT", repo)
    monkeypatch.setattr(dependency_freshness_gate, "POLICY_PATH", repo / "governance" / "security" / "dependency_freshness_policy.json")
    monkeypatch.setattr(dependency_freshness_gate, "LOCK_PATH", repo / "requirements.lock")
    monkeypatch.setattr(dependency_freshness_gate, "evidence_root", lambda: repo / "evidence")
    assert dependency_freshness_gate.main([]) == 0
    report = json.loads((sec / "dependency_freshness_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "PASS"
    assert report["summary"]["active_transitive_vulnerabilities"] == 1


def test_dependency_freshness_gate_fails_when_transitive_vuln_age_exceeds_limit(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    sec = repo / "evidence" / "security"
    (repo / "governance" / "security").mkdir(parents=True)
    (repo / "requirements.lock").write_text("directpkg==1.0.0\n", encoding="utf-8")
    _write_json(
        repo / "governance" / "security" / "dependency_freshness_policy.json",
        {
            "max_known_vulnerable_age_days": 3,
            "enforce_transitive_only": True,
            "fail_on_missing_pip_audit_report": True,
            "history_path": "evidence/security/dependency_vulnerability_freshness_history.json",
        },
    )
    _write_json(
        sec / "pip_audit.json",
        {
            "metadata": {"generated_at_utc": "2026-03-05T00:00:00+00:00"},
            "report": [{"name": "transitivepkg", "vulns": [{"id": "GHSA-old"}]}],
        },
    )
    _write_json(
        sec / "dependency_vulnerability_freshness_history.json",
        {
            "entries": {
                "transitivepkg|GHSA-old": {
                    "package": "transitivepkg",
                    "vulnerability_id": "GHSA-old",
                    "first_seen_utc": "2026-02-20T00:00:00+00:00",
                    "last_seen_utc": "2026-02-20T00:00:00+00:00",
                    "resolved_at_utc": "",
                }
            }
        },
    )

    monkeypatch.setattr(dependency_freshness_gate, "ROOT", repo)
    monkeypatch.setattr(dependency_freshness_gate, "POLICY_PATH", repo / "governance" / "security" / "dependency_freshness_policy.json")
    monkeypatch.setattr(dependency_freshness_gate, "LOCK_PATH", repo / "requirements.lock")
    monkeypatch.setattr(dependency_freshness_gate, "evidence_root", lambda: repo / "evidence")
    assert dependency_freshness_gate.main([]) == 1
    report = json.loads((sec / "dependency_freshness_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("vulnerability_age_exceeded:transitivepkg:GHSA-old") for item in report["findings"])
