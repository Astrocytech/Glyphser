from __future__ import annotations

import json
from pathlib import Path

from tooling.security import security_workflow_contract_gate


def test_security_workflow_contract_gate_passes_when_required_ci_snippets_exist(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    ev = repo / "evidence" / "security"
    wf.mkdir(parents=True)
    ev.mkdir(parents=True)
    ci_text = """
jobs:
  security-matrix:
    permissions:
      security-events: write
    steps:
      - run: python tooling/security/evidence_run_dir_guard.py --run-id x
      - run: python tooling/security/install_security_toolchain.py
      - if: github.event_name != 'pull_request' || github.event.pull_request.head.repo.fork == false
      - run: semgrep --version
      - run: python -c "import pkg_resources"
      - run: python tooling/security/subprocess_allowlist_report.py
      - run: python tooling/security/subprocess_direct_usage_gate.py
      - run: python tooling/security/security_super_gate_manifest_gate.py
      - run: python tooling/security/workflow_artifact_retention_gate.py
      - run: python tooling/security/semgrep_rules_self_check_gate.py
      - run: python tooling/security/workflow_risky_patterns_gate.py
      - run: python tooling/security/workflow_deprecated_invocation_gate.py
      - run: python tooling/security/policy_schema_validation_gate.py
      - run: python tooling/security/security_schema_migration_tracker.py
      - run: python tooling/security/security_evidence_corruption_gate.py
      - run: python tooling/security/security_workflow_trigger_gate.py
      - run: python tooling/security/security_critical_test_wiring_gate.py
      - run: echo semgrep.json
"""
    (wf / "ci.yml").write_text(ci_text, encoding="utf-8")
    maintenance_text = """
jobs:
  security-maintenance:
    steps:
      - run: python tooling/security/install_security_toolchain.py
      - run: python tooling/security/evidence_run_dir_guard.py --run-id x
      - run: semgrep --version
      - run: python -c "import pkg_resources"
      - run: python tooling/security/subprocess_allowlist_report.py
      - run: python tooling/security/subprocess_direct_usage_gate.py
      - run: python tooling/security/security_super_gate_manifest_gate.py
      - run: python tooling/security/workflow_artifact_retention_gate.py
      - run: python tooling/security/semgrep_rules_self_check_gate.py
      - run: python tooling/security/workflow_risky_patterns_gate.py
      - run: python tooling/security/workflow_deprecated_invocation_gate.py
      - run: python tooling/security/policy_schema_validation_gate.py
      - run: python tooling/security/security_schema_migration_tracker.py
      - run: python tooling/security/security_evidence_corruption_gate.py
      - run: python tooling/security/security_workflow_trigger_gate.py
      - run: python tooling/security/security_critical_test_wiring_gate.py
"""
    (wf / "security-maintenance.yml").write_text(maintenance_text, encoding="utf-8")
    extended_text = """
jobs:
  security-super-extended:
    steps:
      - run: python tooling/security/install_security_toolchain.py
      - run: python tooling/security/evidence_run_dir_guard.py --run-id x
      - run: semgrep --version
      - run: python -c "import pkg_resources"
"""
    (wf / "security-super-extended.yml").write_text(extended_text, encoding="utf-8")
    monkeypatch.setattr(security_workflow_contract_gate, "ROOT", repo)
    monkeypatch.setattr(security_workflow_contract_gate, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_contract_gate.main([]) == 0


def test_security_workflow_contract_gate_fails_when_snippet_missing(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    wf = repo / ".github" / "workflows"
    ev = repo / "evidence" / "security"
    wf.mkdir(parents=True)
    ev.mkdir(parents=True)
    (wf / "ci.yml").write_text("jobs:\n  test:\n    runs-on: ubuntu-latest\n", encoding="utf-8")
    (wf / "security-maintenance.yml").write_text("jobs:\n  x:\n    runs-on: ubuntu-latest\n", encoding="utf-8")
    (wf / "security-super-extended.yml").write_text("jobs:\n  y:\n    runs-on: ubuntu-latest\n", encoding="utf-8")
    monkeypatch.setattr(security_workflow_contract_gate, "ROOT", repo)
    monkeypatch.setattr(security_workflow_contract_gate, "evidence_root", lambda: repo / "evidence")
    assert security_workflow_contract_gate.main([]) == 1
    report = json.loads((ev / "security_workflow_contract_gate.json").read_text(encoding="utf-8"))
    assert report["status"] == "FAIL"
    assert any(item.startswith("missing_workflow_contract_snippet:") for item in report["findings"])
