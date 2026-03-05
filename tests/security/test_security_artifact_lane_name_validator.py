from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_artifact_lane_name_validator


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_security_artifact_lane_name_validator_passes_with_job_lane_name(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    _write(
        workflows / "security-maintenance.yml",
        "      - name: Upload\n"
        "        uses: actions/upload-artifact@v4\n"
        "        with:\n"
        "          name: ${{ github.job }}-security-evidence\n",
    )

    monkeypatch.setattr(security_artifact_lane_name_validator, "ROOT", repo)
    monkeypatch.setattr(security_artifact_lane_name_validator, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_artifact_lane_name_validator, "evidence_root", lambda: repo / "evidence")
    assert security_artifact_lane_name_validator.main([]) == 0


def test_security_artifact_lane_name_validator_fails_without_lane_identifier(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    _write(
        workflows / "security-maintenance.yml",
        "      - name: Upload\n"
        "        uses: actions/upload-artifact@v4\n"
        "        with:\n"
        "          name: evidence-bundle\n",
    )

    monkeypatch.setattr(security_artifact_lane_name_validator, "ROOT", repo)
    monkeypatch.setattr(security_artifact_lane_name_validator, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_artifact_lane_name_validator, "evidence_root", lambda: repo / "evidence")
    assert security_artifact_lane_name_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_artifact_lane_name_validator.json").read_text(encoding="utf-8"))
    assert any(item.startswith("artifact_name_missing_lane_identifier:") for item in report["findings"])
