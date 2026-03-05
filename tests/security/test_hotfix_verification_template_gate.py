from __future__ import annotations

import json
from pathlib import Path

from tooling.security import hotfix_verification_template_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_hotfix_verification_template_gate_passes_with_required_sections(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    template = repo / "governance" / "security" / "hotfix_verification_template.md"
    _write(
        template,
        "\n".join(
            [
                "## Before Fix (Failing Test Proof)",
                "- Test command:",
                "- Failure output artifact path:",
                "## After Fix (Passing Test Proof)",
                "- Test command:",
                "- Passing output artifact path:",
            ]
        ),
    )

    monkeypatch.setattr(hotfix_verification_template_gate, "ROOT", repo)
    monkeypatch.setattr(hotfix_verification_template_gate, "TEMPLATE", template)
    monkeypatch.setattr(hotfix_verification_template_gate, "evidence_root", lambda: repo / "evidence")
    assert hotfix_verification_template_gate.main([]) == 0


def test_hotfix_verification_template_gate_fails_when_markers_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    template = repo / "governance" / "security" / "hotfix_verification_template.md"
    _write(template, "## Before Fix (Failing Test Proof)\n")

    monkeypatch.setattr(hotfix_verification_template_gate, "ROOT", repo)
    monkeypatch.setattr(hotfix_verification_template_gate, "TEMPLATE", template)
    monkeypatch.setattr(hotfix_verification_template_gate, "evidence_root", lambda: repo / "evidence")
    assert hotfix_verification_template_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "hotfix_verification_template_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(finding.startswith("missing_hotfix_template_marker:") for finding in report["findings"])
