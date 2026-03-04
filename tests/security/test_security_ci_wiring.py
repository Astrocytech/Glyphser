from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_ci_security_steps_are_wired() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "security-matrix:" in ci
    assert 'python-version: ["3.11", "3.12"]' in ci
    assert "bandit -q -c tooling/security/bandit.yaml -r glyphser runtime tooling -l -ii" in ci
    assert "python tooling/security/pip_audit_gate.py" in ci
    assert "python tooling/security/secret_scan_gate.py" in ci
    assert "python tooling/security/workflow_pinning_gate.py" in ci
    assert "python tooling/security/incident_response_gate.py" in ci
    assert "python tooling/security/org_secret_backend_gate.py" in ci
    assert "python tooling/security/secret_management_gate.py" in ci
    assert "python tooling/security/production_controls_gate.py" in ci
    assert "python tooling/security/third_party_pentest_gate.py" in ci
    assert "python tooling/security/live_integrations_verify.py --dry-run" in ci
    assert "python tooling/security/container_provenance_gate.py" in ci
    assert "python tooling/security/provenance_signature_gate.py" in ci
    assert "python tooling/security/slsa_attestation_gate.py" in ci
    assert "python tooling/security/security_artifacts.py" in ci
    assert "python tooling/security/branch_protection_policy_gate.py" in ci
    assert "bandit -q -c tooling/security/bandit.yaml -r glyphser runtime tooling -f sarif -o bandit.sarif -l -ii" in ci
    assert "semgrep --config tooling/security/semgrep-rules.yml --error --sarif --output semgrep.sarif" in ci
    assert "name: security-artifacts-${{ matrix.python-version }}" in ci
    assert "uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683" in ci


def test_ci_conformance_step_is_wired() -> None:
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    assert "run: python tooling/conformance/cli.py run" in ci
