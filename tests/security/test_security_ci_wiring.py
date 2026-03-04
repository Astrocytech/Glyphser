from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ci_security_steps_are_wired() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "security-matrix:" in ci
    assert 'python-version: ["3.11", "3.12"]' in ci
    assert "bandit==1.9.4" in ci
    assert "pip-audit==2.9.0" in ci
    assert "semgrep==1.95.0" in ci
    assert "setuptools==75.8.0" in ci
    assert (
        "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/security-matrix-${{ matrix.python-version }}" in ci
    )
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in ci
    assert "python tooling/security/policy_signature_gate.py --strict-key" in ci
    assert "python tooling/security/security_toolchain_gate.py" in ci
    assert "python tooling/security/subprocess_allowlist_report.py" in ci
    assert "python tooling/security/security_workflow_contract_gate.py" in ci
    assert "python tooling/security/security_workflow_trigger_gate.py" in ci
    assert "python tooling/security/security_critical_test_wiring_gate.py" in ci
    assert "python tooling/security/security_sarif_permissions_gate.py" in ci
    assert "python tooling/security/security_workflow_permissions_policy_gate.py" in ci
    assert "python tooling/security/security_exception_suppression_gate.py" in ci
    assert "python tooling/security/security_dead_gate_wiring_gate.py" in ci
    assert "python tooling/security/hardening_todo_consistency_gate.py" in ci
    assert "bandit -q -c tooling/security/bandit.yaml -r glyphser runtime tooling -l -ii" in ci
    assert "python tooling/security/pip_audit_gate.py" in ci
    assert "python tooling/security/secret_scan_gate.py" in ci
    assert "python tooling/security/workflow_pinning_gate.py" in ci
    assert "python tooling/security/incident_response_gate.py" in ci
    assert "python tooling/security/org_secret_backend_gate.py" in ci
    assert "python tooling/security/secret_management_gate.py" in ci
    assert "python tooling/security/production_controls_gate.py" in ci
    assert "python tooling/security/third_party_pentest_gate.py --strict-key" in ci
    assert "python tooling/security/live_integrations_verify.py --dry-run" in ci
    assert "python tooling/security/live_rollout_gate.py --allow-dry-run --allow-missing" in ci
    assert "python tooling/security/container_provenance_gate.py" in ci
    assert "python tooling/security/abuse_telemetry_snapshot.py" in ci
    assert "python tooling/security/abuse_telemetry_gate.py" in ci
    assert "python tooling/security/security_gate_test_coverage_gate.py" in ci
    assert "python tooling/security/evidence_attestation_index.py --strict-key" in ci
    assert "python tooling/security/evidence_attestation_gate.py --strict-key" in ci
    assert "python tooling/security/provenance_signature_gate.py --strict-key" in ci
    assert "python tooling/security/slsa_attestation_gate.py" in ci
    assert "python tooling/security/workflow_evidence_scope_gate.py" in ci
    assert "python tooling/security/conformance_security_coupling_gate.py" in ci
    assert "python tooling/security/security_super_gate.py --strict-key" in ci
    assert "python tooling/security/security_artifacts.py" in ci
    assert "python tooling/security/branch_protection_policy_gate.py" in ci
    assert "bandit -q -c tooling/security/bandit.yaml -r glyphser runtime tooling -f json -o bandit.json -l -ii" in ci
    assert "python tooling/security/bandit_json_to_sarif.py --input bandit.json --output bandit.sarif" in ci
    assert "semgrep --config tooling/security/semgrep-rules.yml --error --sarif --output semgrep.sarif" in ci
    assert "pytest -q tests/security" in ci
    assert "semgrep --version" in ci
    assert 'python -c "import pkg_resources"' in ci
    assert "name: security-artifacts-${{ matrix.python-version }}" in ci
    assert "uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683" in ci


def test_ci_conformance_step_is_wired() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "run: python tooling/conformance/cli.py run" in ci
