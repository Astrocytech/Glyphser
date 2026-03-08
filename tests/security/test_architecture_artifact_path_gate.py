from __future__ import annotations

import json
from pathlib import Path

from tooling.security import architecture_artifact_path_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_architecture_artifact_path_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / "docs" / "ARCHITECTURE.md", "Artifact: `evidence/security/security_super_gate.json`\n")
    _write(repo / "governance" / "security" / "SECURITY_ARCHITECTURE.md", "Artifact: `evidence/security/policy_signature.json`\n")
    _write(repo / "governance" / "security" / "EVIDENCE_FLOW_ARCHITECTURE.md", "Artifact: `security_verification_summary.json`\n")
    for wf in ("ci.yml", "security-maintenance.yml", "release.yml"):
        _write(
            repo / ".github" / "workflows" / wf,
            "path: ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/security_super_gate.json\n"
            "path: ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/policy_signature.json\n"
            "path: ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/security_verification_summary.json\n",
        )
    monkeypatch.setattr(architecture_artifact_path_gate, "ROOT", repo)
    monkeypatch.setattr(
        architecture_artifact_path_gate,
        "ARCH_DOCS",
        (
            repo / "docs" / "ARCHITECTURE.md",
            repo / "governance" / "security" / "SECURITY_ARCHITECTURE.md",
            repo / "governance" / "security" / "EVIDENCE_FLOW_ARCHITECTURE.md",
        ),
    )
    monkeypatch.setattr(
        architecture_artifact_path_gate,
        "WORKFLOWS",
        (
            repo / ".github" / "workflows" / "ci.yml",
            repo / ".github" / "workflows" / "security-maintenance.yml",
            repo / ".github" / "workflows" / "release.yml",
        ),
    )
    monkeypatch.setattr(architecture_artifact_path_gate, "evidence_root", lambda: repo / "evidence")
    assert architecture_artifact_path_gate.main([]) == 0


def test_architecture_artifact_path_gate_fails_on_unmapped_path(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _write(repo / "docs" / "ARCHITECTURE.md", "Artifact: `evidence/security/missing_artifact.json`\n")
    _write(repo / "governance" / "security" / "SECURITY_ARCHITECTURE.md", "none\n")
    _write(repo / "governance" / "security" / "EVIDENCE_FLOW_ARCHITECTURE.md", "none\n")
    for wf in ("ci.yml", "security-maintenance.yml", "release.yml"):
        _write(repo / ".github" / "workflows" / wf, "path: ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/security_super_gate.json\n")
    monkeypatch.setattr(architecture_artifact_path_gate, "ROOT", repo)
    monkeypatch.setattr(
        architecture_artifact_path_gate,
        "ARCH_DOCS",
        (
            repo / "docs" / "ARCHITECTURE.md",
            repo / "governance" / "security" / "SECURITY_ARCHITECTURE.md",
            repo / "governance" / "security" / "EVIDENCE_FLOW_ARCHITECTURE.md",
        ),
    )
    monkeypatch.setattr(
        architecture_artifact_path_gate,
        "WORKFLOWS",
        (
            repo / ".github" / "workflows" / "ci.yml",
            repo / ".github" / "workflows" / "security-maintenance.yml",
            repo / ".github" / "workflows" / "release.yml",
        ),
    )
    monkeypatch.setattr(architecture_artifact_path_gate, "evidence_root", lambda: repo / "evidence")
    assert architecture_artifact_path_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "architecture_artifact_path_gate.json").read_text(encoding="utf-8"))
    assert any(item.startswith("architecture_artifact_path_unmapped:") for item in report["findings"])
