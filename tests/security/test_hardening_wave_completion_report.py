from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hardening_wave_completion_report


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_hardening_wave_completion_report_fails_when_requirements_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(hardening_wave_completion_report, "ROOT", repo)
    monkeypatch.setattr(hardening_wave_completion_report, "POLICY", repo / "governance" / "security" / "hardening_execution_waves.json")
    monkeypatch.setattr(hardening_wave_completion_report, "evidence_root", lambda: repo / "evidence")
    assert hardening_wave_completion_report.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hardening_wave_completion_report.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"


def test_hardening_wave_completion_report_passes_with_expected_files(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    policy = repo / "governance" / "security" / "hardening_execution_waves.json"
    _write_json(
        policy,
        {
            "waves": {
                "wave_a": {
                    "checks": [
                        {"type": "file_exists", "path": "tooling/security/a.py"},
                        {"type": "file_contains", "path": ".github/workflows/security.yml", "snippet": "run-security"},
                    ]
                },
                "wave_b": {"checks": [{"type": "file_exists", "path": "governance/security/b.json"}]},
            }
        },
    )
    for rel, content in {
        "tooling/security/a.py": "# ok\n",
        ".github/workflows/security.yml": "run-security\n",
        "governance/security/b.json": "{}\n",
    }.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    monkeypatch.setattr(hardening_wave_completion_report, "ROOT", repo)
    monkeypatch.setattr(hardening_wave_completion_report, "POLICY", policy)
    monkeypatch.setattr(hardening_wave_completion_report, "evidence_root", lambda: repo / "evidence")
    assert hardening_wave_completion_report.main([]) == 0
