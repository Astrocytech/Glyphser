from __future__ import annotations

import hashlib
import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import security_rule_baseline_gate


def _write_approval(repo: Path, diff_sha: str) -> None:
    approval = repo / "governance" / "security" / "security_rule_diff_approval.json"
    approval.parent.mkdir(parents=True, exist_ok=True)
    approval.write_text(
        json.dumps(
            {
                "ticket": "SEC-RULE-123",
                "rationale": "Approved security rule updates.",
                "approved_by": "security-ops",
                "approved_at_utc": "2026-03-01T00:00:00+00:00",
                "expires_at_utc": "2099-01-01T00:00:00+00:00",
                "rule_diff_sha256": diff_sha,
            }
        )
        + "\n",
        encoding="utf-8",
    )
    approval.with_suffix(".json.sig").write_text(
        sign_file(approval, key=current_key(strict=False)) + "\n",
        encoding="utf-8",
    )


def test_security_rule_baseline_gate_skips_when_no_rule_changes(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(security_rule_baseline_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_rule_baseline_gate,
        "APPROVAL_FILE",
        repo / "governance/security/security_rule_diff_approval.json",
    )
    monkeypatch.setattr(security_rule_baseline_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_rule_baseline_gate, "_rules_diff", lambda: "")
    monkeypatch.setattr(security_rule_baseline_gate, "_changed_files", lambda: [])
    assert security_rule_baseline_gate.main([]) == 0


def test_security_rule_baseline_gate_fails_without_signed_approval(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(security_rule_baseline_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_rule_baseline_gate,
        "APPROVAL_FILE",
        repo / "governance/security/security_rule_diff_approval.json",
    )
    monkeypatch.setattr(security_rule_baseline_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_rule_baseline_gate, "_rules_diff", lambda: "diff --git a/x b/x\n+rule\n")
    monkeypatch.setattr(security_rule_baseline_gate, "_changed_files", lambda: ["tooling/security/semgrep-rules.yml"])
    assert security_rule_baseline_gate.main([]) == 1


def test_security_rule_baseline_gate_passes_with_signed_matching_diff_approval(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    diff_text = "diff --git a/tooling/security/semgrep-rules.yml b/tooling/security/semgrep-rules.yml\n+new-rule\n"
    _write_approval(repo, hashlib.sha256(diff_text.encode("utf-8")).hexdigest())

    monkeypatch.setattr(security_rule_baseline_gate, "ROOT", repo)
    monkeypatch.setattr(
        security_rule_baseline_gate,
        "APPROVAL_FILE",
        repo / "governance/security/security_rule_diff_approval.json",
    )
    monkeypatch.setattr(security_rule_baseline_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setattr(security_rule_baseline_gate, "_rules_diff", lambda: diff_text)
    monkeypatch.setattr(
        security_rule_baseline_gate,
        "_changed_files",
        lambda: [
            "tooling/security/semgrep-rules.yml",
            "governance/security/security_rule_diff_approval.json",
            "governance/security/security_rule_diff_approval.json.sig",
        ],
    )
    assert security_rule_baseline_gate.main([]) == 0
