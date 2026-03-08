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
        "          name: ${{ github.job }}-${{ github.run_id }}-security-evidence\n",
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


def test_security_artifact_lane_name_validator_fails_on_duplicate_static_names(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    body = (
        "      - name: Upload\n"
        "        uses: actions/upload-artifact@v4\n"
        "        with:\n"
        "          name: security-artifacts\n"
    )
    _write(workflows / "security-maintenance.yml", body)
    _write(workflows / "security-ci.yml", body)

    monkeypatch.setattr(security_artifact_lane_name_validator, "ROOT", repo)
    monkeypatch.setattr(security_artifact_lane_name_validator, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_artifact_lane_name_validator, "evidence_root", lambda: repo / "evidence")
    assert security_artifact_lane_name_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_artifact_lane_name_validator.json").read_text(encoding="utf-8"))
    assert any(item.startswith("duplicate_artifact_name_across_workflows:security-artifacts:") for item in report["findings"])


def test_security_artifact_lane_name_validator_fails_without_run_discriminator(monkeypatch, tmp_path: Path) -> None:
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
    assert security_artifact_lane_name_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_artifact_lane_name_validator.json").read_text(encoding="utf-8"))
    assert any(item.startswith("artifact_name_missing_run_discriminator:") for item in report["findings"])


def test_security_artifact_lane_name_validator_fails_for_hidden_or_ambiguous_paths(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    _write(
        workflows / "security-maintenance.yml",
        "      - name: Upload\n"
        "        uses: actions/upload-artifact@v4\n"
        "        with:\n"
        "          name: ${{ github.job }}-${{ github.run_id }}-security-evidence\n"
        "          path: |\n"
        "            evidence/security/.secret.json\n"
        "            evidence/security/output.tmp\n",
    )
    monkeypatch.setattr(security_artifact_lane_name_validator, "ROOT", repo)
    monkeypatch.setattr(security_artifact_lane_name_validator, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_artifact_lane_name_validator, "evidence_root", lambda: repo / "evidence")
    assert security_artifact_lane_name_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_artifact_lane_name_validator.json").read_text(encoding="utf-8"))
    assert any(item.startswith("hidden_artifact_path:") for item in report["findings"])
    assert any(item.startswith("ambiguous_artifact_extension:") for item in report["findings"])


def test_security_artifact_lane_name_validator_fails_for_signature_basename_mismatch(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    _write(
        workflows / "security-maintenance.yml",
        "      - name: Upload\n"
        "        uses: actions/upload-artifact@v4\n"
        "        with:\n"
        "          name: ${{ github.job }}-${{ github.run_id }}-security-evidence\n"
        "          path: |\n"
        "            evidence/security/toolchain.sig\n",
    )
    monkeypatch.setattr(security_artifact_lane_name_validator, "ROOT", repo)
    monkeypatch.setattr(security_artifact_lane_name_validator, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_artifact_lane_name_validator, "evidence_root", lambda: repo / "evidence")
    assert security_artifact_lane_name_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_artifact_lane_name_validator.json").read_text(encoding="utf-8"))
    assert any(item.startswith("signature_basename_mismatch:") for item in report["findings"])


def test_security_artifact_lane_name_validator_fails_for_unpaired_signature(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    workflows = repo / ".github" / "workflows"
    _write(
        workflows / "security-maintenance.yml",
        "      - name: Upload\n"
        "        uses: actions/upload-artifact@v4\n"
        "        with:\n"
        "          name: ${{ github.job }}-${{ github.run_id }}-security-evidence\n"
        "          path: |\n"
        "            evidence/security/alpha.json.sig\n",
    )
    monkeypatch.setattr(security_artifact_lane_name_validator, "ROOT", repo)
    monkeypatch.setattr(security_artifact_lane_name_validator, "WORKFLOWS_DIR", workflows)
    monkeypatch.setattr(security_artifact_lane_name_validator, "evidence_root", lambda: repo / "evidence")
    assert security_artifact_lane_name_validator.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "security_artifact_lane_name_validator.json").read_text(encoding="utf-8"))
    assert any(item.startswith("signature_without_matching_artifact:") for item in report["findings"])
