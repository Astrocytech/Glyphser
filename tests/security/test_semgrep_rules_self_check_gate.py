from __future__ import annotations

import json
from pathlib import Path

from tooling.security import semgrep_rules_self_check_gate


def test_semgrep_rules_self_check_gate_passes_with_expected_ids(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    rules = sec / "semgrep-rules.yml"
    content = "rules:\n" + "".join(f"  - id: {rid}\n" for rid in sorted(semgrep_rules_self_check_gate.EXPECTED_RULE_IDS))
    rules.write_text(content, encoding="utf-8")
    monkeypatch.setattr(semgrep_rules_self_check_gate, "ROOT", repo)
    monkeypatch.setattr(semgrep_rules_self_check_gate, "RULES_FILE", rules)
    monkeypatch.setattr(semgrep_rules_self_check_gate, "evidence_root", lambda: repo / "evidence")
    assert semgrep_rules_self_check_gate.main([]) == 0


def test_semgrep_rules_self_check_gate_fails_on_missing_ids(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path
    sec = repo / "tooling" / "security"
    sec.mkdir(parents=True)
    ev = repo / "evidence" / "security"
    ev.mkdir(parents=True)
    rules = sec / "semgrep-rules.yml"
    rules.write_text("rules:\n  - id: glyphser.subprocess-shell-true\n", encoding="utf-8")
    monkeypatch.setattr(semgrep_rules_self_check_gate, "ROOT", repo)
    monkeypatch.setattr(semgrep_rules_self_check_gate, "RULES_FILE", rules)
    monkeypatch.setattr(semgrep_rules_self_check_gate, "evidence_root", lambda: repo / "evidence")
    assert semgrep_rules_self_check_gate.main([]) == 1
    report = json.loads((ev / "semgrep_rules_self_check_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("missing_expected_rule_id:") for item in report["findings"])
