from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import workflow_change_management_gate


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_structure_approval(repo: Path, *, with_signature: bool = True) -> None:
    approval = repo / "governance" / "security" / "workflow_structure_change_approval.json"
    approval.parent.mkdir(parents=True, exist_ok=True)
    approval.write_text(
        json.dumps(
            {
                "ticket": "SEC-123",
                "rationale": "Approved structural workflow change.",
                "approved_by": "security-ops",
                "approved_at_utc": "2026-03-01T00:00:00+00:00",
                "expires_at_utc": "2099-01-01T00:00:00+00:00",
                "workflow_paths": [".github/workflows/security-maintenance.yml"],
            },
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    if with_signature:
        approval.with_suffix(".json.sig").write_text(sign_file(approval, key=current_key(strict=False)) + "\n", encoding="utf-8")


def test_workflow_change_management_gate_fails_without_policy_diff_or_rationale(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", ".github/workflows/security-maintenance.yml")
    monkeypatch.delenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", raising=False)
    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert report["status"] == "FAIL"
    assert "security_workflow_change_missing_policy_diff_or_rationale" in report["findings"]


def test_workflow_change_management_gate_passes_with_policy_diff(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv(
        "GLYPHSER_CHANGED_FILES",
        ".github/workflows/security-maintenance.yml,governance/security/promotion_policy.json",
    )
    monkeypatch.delenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", raising=False)
    _write(
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
        '{"step_order_checks":[{"workflow":".github/workflows/security-maintenance.yml","ordered_steps":["A","B"]}]}\n',
    )
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        "jobs:\n  x:\n    steps:\n      - name: A\n      - name: B\n",
    )
    assert workflow_change_management_gate.main([]) == 0


def test_workflow_change_management_gate_fails_on_step_order_violation(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", "governance/security/promotion_policy.json")
    monkeypatch.delenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", raising=False)
    _write(
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
        '{"step_order_checks":[{"workflow":".github/workflows/security-maintenance.yml","ordered_steps":["A","B"]}]}\n',
    )
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        "jobs:\n  x:\n    steps:\n      - name: B\n      - name: A\n",
    )

    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert "workflow_dependency_order_violation:.github/workflows/security-maintenance.yml:A>B" in report["findings"]


def test_workflow_change_management_gate_fails_when_required_env_var_missing(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", "governance/security/promotion_policy.json")
    monkeypatch.delenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", raising=False)
    _write(
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
        '{"step_order_checks":[{"workflow":".github/workflows/security-maintenance.yml","ordered_steps":["A","B"]}],"required_env_checks":[{"workflow":".github/workflows/security-maintenance.yml","required_env_vars":["GLYPHSER_EVIDENCE_ROOT"]}]}\n',
    )
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        "jobs:\n  x:\n    steps:\n      - name: A\n      - name: B\n",
    )

    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert "missing_required_env_var:.github/workflows/security-maintenance.yml:GLYPHSER_EVIDENCE_ROOT" in report["findings"]


def test_workflow_change_management_gate_fails_on_artifact_upload_path_drift(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", "governance/security/promotion_policy.json")
    monkeypatch.delenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", raising=False)
    _write(
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
        '{"step_order_checks":[{"workflow":".github/workflows/security-maintenance.yml","ordered_steps":["A","B"]}],"artifact_upload_path_baselines":[{"workflow":".github/workflows/security-maintenance.yml","baseline":"governance/security/upload_baseline.json"}]}\n',
    )
    _write(
        repo / "governance" / "security" / "upload_baseline.json",
        '{"upload_paths":["${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/a.json"]}\n',
    )
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        "jobs:\n  x:\n    steps:\n      - name: A\n      - name: B\n      - name: Upload\n        with:\n          path: |\n            ${{ env.GLYPHSER_EVIDENCE_ROOT }}/security/b.json\n",
    )

    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert "artifact_upload_paths_drift:.github/workflows/security-maintenance.yml" in report["findings"]


def test_workflow_change_management_gate_fails_on_matrix_shrinkage(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", "governance/security/promotion_policy.json")
    monkeypatch.delenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", raising=False)
    _write(
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
        '{"step_order_checks":[{"workflow":".github/workflows/security-maintenance.yml","ordered_steps":["A","B"]}],"matrix_minimums":[{"workflow":".github/workflows/security-maintenance.yml","key":"python-version","minimum_entries":2,"required_values":["3.11","3.12"]}]}\n',
    )
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        "jobs:\n  x:\n    strategy:\n      matrix:\n        python-version: [\"3.11\"]\n    steps:\n      - name: A\n      - name: B\n",
    )

    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert "matrix_shrinkage_detected:.github/workflows/security-maintenance.yml:python-version:1<2" in report["findings"]
    assert "matrix_required_value_missing:.github/workflows/security-maintenance.yml:python-version:3.12" in report["findings"]


def test_workflow_change_management_gate_fails_on_step_structure_drift_without_signed_approval(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STEP_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STRUCTURE_APPROVAL_FILE",
        repo / "governance" / "security" / "workflow_structure_change_approval.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", ".github/workflows/security-maintenance.yml")
    monkeypatch.setenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "SEC-123 approved")

    _write(repo / "governance" / "security" / "security_workflow_dependency_policy.json", "{}\n")
    _write(
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
        json.dumps(
            {
                "workflows": {
                    ".github/workflows/security-maintenance.yml": {
                        "jobs": {"audit": ["Step A", "Step B"]},
                    }
                }
            }
        )
        + "\n",
    )
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        "jobs:\n  audit:\n    steps:\n      - name: Step A\n      - name: Step X\n      - name: Step B\n",
    )

    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert any(
        item.startswith(
            "security_step_structure_drift:.github/workflows/security-maintenance.yml:audit:inserted=Step X"
        )
        for item in report["findings"]
    )
    assert "missing_updated_workflow_structure_change_approval_file" in report["findings"]


def test_workflow_change_management_gate_passes_on_step_structure_drift_with_signed_approval(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STEP_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STRUCTURE_APPROVAL_FILE",
        repo / "governance" / "security" / "workflow_structure_change_approval.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv(
        "GLYPHSER_CHANGED_FILES",
        (
            ".github/workflows/security-maintenance.yml,"
            "governance/security/workflow_structure_change_approval.json,"
            "governance/security/workflow_structure_change_approval.json.sig"
        ),
    )
    monkeypatch.setenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "SEC-123 approved")

    _write(
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
        "{}\n",
    )
    _write(
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
        json.dumps(
            {
                "workflows": {
                    ".github/workflows/security-maintenance.yml": {
                        "jobs": {"audit": ["Step A", "Step B"]},
                    }
                }
            }
        )
        + "\n",
    )
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        "jobs:\n  audit:\n    steps:\n      - name: Step A\n      - name: Step X\n      - name: Step B\n",
    )
    _write_structure_approval(repo)

    assert workflow_change_management_gate.main([]) == 0


def test_workflow_change_management_gate_fails_on_critical_step_condition_drift_without_signed_approval(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STEP_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "CONDITION_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_critical_step_conditions.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STRUCTURE_APPROVAL_FILE",
        repo / "governance" / "security" / "workflow_structure_change_approval.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", ".github/workflows/security-maintenance.yml")
    monkeypatch.setenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "SEC-456 approved")

    _write(
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
        "{}\n",
    )
    _write(repo / "governance" / "security" / "security_workflow_job_step_baseline.json", '{"workflows":{}}\n')
    _write(
        repo / "governance" / "security" / "security_workflow_critical_step_conditions.json",
        json.dumps(
            {
                "critical_step_conditions": [
                    {
                        "workflow": ".github/workflows/security-maintenance.yml",
                        "job": "audit",
                        "step": "Upload SARIF to Code Scanning",
                        "if": "github.event_name == 'push'",
                    }
                ]
            }
        )
        + "\n",
    )
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        (
            "jobs:\n"
            "  audit:\n"
            "    steps:\n"
            "      - name: Upload SARIF to Code Scanning\n"
            "        if: always()\n"
            "        run: echo upload\n"
        ),
    )

    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert any(
        item.startswith(
            "critical_step_condition_drift:.github/workflows/security-maintenance.yml:audit:Upload SARIF to Code Scanning"
        )
        for item in report["findings"]
    )
    assert "missing_updated_workflow_structure_change_approval_file" in report["findings"]


def test_workflow_change_management_gate_passes_on_critical_step_condition_drift_with_signed_approval(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STEP_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "CONDITION_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_critical_step_conditions.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STRUCTURE_APPROVAL_FILE",
        repo / "governance" / "security" / "workflow_structure_change_approval.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv(
        "GLYPHSER_CHANGED_FILES",
        (
            ".github/workflows/security-maintenance.yml,"
            "governance/security/workflow_structure_change_approval.json,"
            "governance/security/workflow_structure_change_approval.json.sig"
        ),
    )
    monkeypatch.setenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "SEC-456 approved")

    _write(repo / "governance" / "security" / "security_workflow_dependency_policy.json", "{}\n")
    _write(repo / "governance" / "security" / "security_workflow_job_step_baseline.json", '{"workflows":{}}\n')
    _write(
        repo / "governance" / "security" / "security_workflow_critical_step_conditions.json",
        json.dumps(
            {
                "critical_step_conditions": [
                    {
                        "workflow": ".github/workflows/security-maintenance.yml",
                        "job": "audit",
                        "step": "Upload SARIF to Code Scanning",
                        "if": "github.event_name == 'push'",
                    }
                ]
            }
        )
        + "\n",
    )
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        (
            "jobs:\n"
            "  audit:\n"
            "    steps:\n"
            "      - name: Upload SARIF to Code Scanning\n"
            "        if: always()\n"
            "        run: echo upload\n"
        ),
    )
    _write_structure_approval(repo)

    assert workflow_change_management_gate.main([]) == 0


def test_workflow_change_management_gate_fails_on_shell_option_weakening(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STEP_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "CONDITION_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_critical_step_conditions.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", ".github/workflows/security-maintenance.yml")
    monkeypatch.setenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "SEC-789 approved")

    _write(repo / "governance" / "security" / "security_workflow_dependency_policy.json", "{}\n")
    _write(repo / "governance" / "security" / "security_workflow_job_step_baseline.json", '{"workflows":{}}\n')
    _write(repo / "governance" / "security" / "security_workflow_critical_step_conditions.json", '{"critical_step_conditions":[]}\n')
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        (
            "jobs:\n"
            "  audit:\n"
            "    steps:\n"
            "      - name: Weak shell step\n"
            "        run: |\n"
            "          set +e\n"
            "          semgrep --version | cat\n"
            "          ./script.sh || true\n"
        ),
    )

    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert "security_shell_option_weakening_set_plus_e:.github/workflows/security-maintenance.yml:audit:Weak shell step" in report["findings"]
    assert "security_shell_option_weakening_unchecked_pipe:.github/workflows/security-maintenance.yml:audit:Weak shell step" in report["findings"]
    assert "security_shell_option_weakening_ignored_return:.github/workflows/security-maintenance.yml:audit:Weak shell step" in report["findings"]


def test_workflow_change_management_gate_passes_with_strict_shell_options(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STEP_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "CONDITION_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_critical_step_conditions.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", ".github/workflows/security-maintenance.yml")
    monkeypatch.setenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "SEC-789 approved")

    _write(repo / "governance" / "security" / "security_workflow_dependency_policy.json", "{}\n")
    _write(repo / "governance" / "security" / "security_workflow_job_step_baseline.json", '{"workflows":{}}\n')
    _write(repo / "governance" / "security" / "security_workflow_critical_step_conditions.json", '{"critical_step_conditions":[]}\n')
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        (
            "jobs:\n"
            "  audit:\n"
            "    steps:\n"
            "      - name: Strict shell step\n"
            "        run: |\n"
            "          set -euo pipefail\n"
            "          semgrep --version | cat\n"
        ),
    )

    assert workflow_change_management_gate.main([]) == 0


def test_workflow_change_management_gate_fails_when_cwd_or_trusted_context_missing(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STEP_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "CONDITION_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_critical_step_conditions.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", ".github/workflows/security-maintenance.yml")
    monkeypatch.setenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "SEC-902 approved")

    _write(
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
        '{"trusted_context_checks":[".github/workflows/security-maintenance.yml"]}\n',
    )
    _write(repo / "governance" / "security" / "security_workflow_job_step_baseline.json", '{"workflows":{}}\n')
    _write(repo / "governance" / "security" / "security_workflow_critical_step_conditions.json", '{"critical_step_conditions":[]}\n')
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        (
            "jobs:\n"
            "  audit:\n"
            "    steps:\n"
            "      - uses: actions/checkout@v4\n"
            "      - name: Security step\n"
            "        run: echo hi\n"
        ),
    )

    assert workflow_change_management_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "workflow_change_management_gate.json").read_text("utf-8"))
    assert "security_workflow_missing_trusted_repo_context:.github/workflows/security-maintenance.yml" in report["findings"]
    assert "security_step_missing_explicit_cwd:.github/workflows/security-maintenance.yml:audit:Security step" in report["findings"]


def test_workflow_change_management_gate_passes_with_explicit_cwd_and_pinned_checkout(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    monkeypatch.setattr(workflow_change_management_gate, "ROOT", repo)
    monkeypatch.setattr(
        workflow_change_management_gate,
        "DEPENDENCY_POLICY",
        repo / "governance" / "security" / "security_workflow_dependency_policy.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "STEP_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_job_step_baseline.json",
    )
    monkeypatch.setattr(
        workflow_change_management_gate,
        "CONDITION_BASELINE_FILE",
        repo / "governance" / "security" / "security_workflow_critical_step_conditions.json",
    )
    monkeypatch.setattr(workflow_change_management_gate, "evidence_root", lambda: repo / "evidence")
    monkeypatch.setenv("GLYPHSER_CHANGED_FILES", ".github/workflows/security-maintenance.yml")
    monkeypatch.setenv("GLYPHSER_WORKFLOW_CHANGE_RATIONALE", "SEC-902 approved")

    _write(repo / "governance" / "security" / "security_workflow_dependency_policy.json", "{}\n")
    _write(repo / "governance" / "security" / "security_workflow_job_step_baseline.json", '{"workflows":{}}\n')
    _write(repo / "governance" / "security" / "security_workflow_critical_step_conditions.json", '{"critical_step_conditions":[]}\n')
    _write(
        repo / ".github" / "workflows" / "security-maintenance.yml",
        (
            "jobs:\n"
            "  audit:\n"
            "    steps:\n"
            "      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683\n"
            "      - name: Security step\n"
            "        working-directory: .\n"
            "        run: echo hi\n"
        ),
    )

    assert workflow_change_management_gate.main([]) == 0
