from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_artifact_signature_coverage_gate


def _write_policy(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "required_signature_pairs": [
                    {"artifact": "sbom.json", "signature": "sbom.json.sig"},
                    {"artifact": "build_provenance.json", "signature": "build_provenance.json.sig"},
                ]
            }
        )
        + "\n",
        encoding="utf-8",
    )


def test_security_artifact_signature_coverage_gate_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    _write_policy(repo / "governance" / "security" / "security_artifact_signature_policy.json")
    (wf / "ci.yml").write_text(
        "\n".join(
            [
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - uses: actions/upload-artifact@abc",
                "        with:",
                "          path: |",
                "            ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/sbom.json",
                "            ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/sbom.json.sig",
                "            ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/build_provenance.json",
                "            ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/build_provenance.json.sig",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_artifact_signature_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(security_artifact_signature_coverage_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(
        security_artifact_signature_coverage_gate,
        "POLICY",
        repo / "governance" / "security" / "security_artifact_signature_policy.json",
    )
    monkeypatch.setattr(security_artifact_signature_coverage_gate, "evidence_root", lambda: repo / "evidence")
    assert security_artifact_signature_coverage_gate.main([]) == 0


def test_security_artifact_signature_coverage_gate_fails_when_sig_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    _write_policy(repo / "governance" / "security" / "security_artifact_signature_policy.json")
    (wf / "ci.yml").write_text(
        "\n".join(
            [
                "jobs:",
                "  security-matrix:",
                "    steps:",
                "      - uses: actions/upload-artifact@abc",
                "        with:",
                "          path: |",
                "            ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/sbom.json",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(security_artifact_signature_coverage_gate, "ROOT", repo)
    monkeypatch.setattr(security_artifact_signature_coverage_gate, "WORKFLOWS", wf)
    monkeypatch.setattr(
        security_artifact_signature_coverage_gate,
        "POLICY",
        repo / "governance" / "security" / "security_artifact_signature_policy.json",
    )
    monkeypatch.setattr(security_artifact_signature_coverage_gate, "evidence_root", lambda: repo / "evidence")
    assert security_artifact_signature_coverage_gate.main([]) == 1
    report = json.loads(
        (repo / "evidence" / "security" / "security_artifact_signature_coverage_gate.json").read_text("utf-8")
    )
    assert report["status"] == "FAIL"
    assert any(str(item).startswith("missing_signature_upload:") for item in report["findings"])
