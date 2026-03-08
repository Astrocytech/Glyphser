from __future__ import annotations

import json
from pathlib import Path

from tooling.security import annual_independent_review_attestation


def _write(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload) + "\n", encoding="utf-8")


def _seed_checklist_and_policy(repo: Path) -> None:
    (repo / "governance" / "security").mkdir(parents=True, exist_ok=True)
    (repo / "product" / "handbook" / "policies").mkdir(parents=True, exist_ok=True)
    (repo / "governance" / "security" / "ANNUAL_INDEPENDENT_REVIEW_CHECKLIST.md").write_text(
        "\n".join(
            [
                "- reviewer independence",
                "- scope",
                "- findings",
                "- signed annual independent review attestation",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (repo / "product" / "handbook" / "policies" / "ANNUAL_SECURITY_REVIEW_POLICY.md").write_text(
        "# Annual Security Review Policy\n",
        encoding="utf-8",
    )


def test_annual_independent_review_attestation_passes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _seed_checklist_and_policy(repo)
    _write(repo / "evidence" / "security" / "formal_security_review_artifact.json", {"status": "PASS"})
    _write(repo / "evidence" / "security" / "security_super_gate.json", {"status": "PASS"})
    _write(repo / "evidence" / "security" / "security_verification_summary.json", {"status": "PASS"})

    monkeypatch.setenv("GLYPHSER_INDEPENDENT_REVIEWER", "reviewer@example.test")
    monkeypatch.setenv("GLYPHSER_INDEPENDENT_REVIEW_APPROVER", "approver@example.test")
    monkeypatch.setattr(annual_independent_review_attestation, "ROOT", repo)
    monkeypatch.setattr(
        annual_independent_review_attestation,
        "CHECKLIST",
        repo / "governance" / "security" / "ANNUAL_INDEPENDENT_REVIEW_CHECKLIST.md",
    )
    monkeypatch.setattr(
        annual_independent_review_attestation,
        "POLICY",
        repo / "product" / "handbook" / "policies" / "ANNUAL_SECURITY_REVIEW_POLICY.md",
    )
    monkeypatch.setattr(annual_independent_review_attestation, "evidence_root", lambda: repo / "evidence")
    assert annual_independent_review_attestation.main([]) == 0
    assert (repo / "evidence" / "security" / "annual_independent_review_attestation.json.sig").exists()


def test_annual_independent_review_attestation_fails_without_checklist(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / "product" / "handbook" / "policies").mkdir(parents=True, exist_ok=True)
    (repo / "product" / "handbook" / "policies" / "ANNUAL_SECURITY_REVIEW_POLICY.md").write_text(
        "# Annual Security Review Policy\n",
        encoding="utf-8",
    )
    _write(repo / "evidence" / "security" / "formal_security_review_artifact.json", {"status": "PASS"})
    _write(repo / "evidence" / "security" / "security_super_gate.json", {"status": "PASS"})
    _write(repo / "evidence" / "security" / "security_verification_summary.json", {"status": "PASS"})

    monkeypatch.setenv("GLYPHSER_INDEPENDENT_REVIEWER", "reviewer@example.test")
    monkeypatch.setenv("GLYPHSER_INDEPENDENT_REVIEW_APPROVER", "approver@example.test")
    monkeypatch.setattr(annual_independent_review_attestation, "ROOT", repo)
    monkeypatch.setattr(
        annual_independent_review_attestation,
        "CHECKLIST",
        repo / "governance" / "security" / "ANNUAL_INDEPENDENT_REVIEW_CHECKLIST.md",
    )
    monkeypatch.setattr(
        annual_independent_review_attestation,
        "POLICY",
        repo / "product" / "handbook" / "policies" / "ANNUAL_SECURITY_REVIEW_POLICY.md",
    )
    monkeypatch.setattr(annual_independent_review_attestation, "evidence_root", lambda: repo / "evidence")
    assert annual_independent_review_attestation.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "annual_independent_review_attestation.json").read_text(encoding="utf-8"))
    assert "missing_annual_independent_review_checklist" in report["findings"]

