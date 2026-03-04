from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_release_workflow_enforces_signature_verification() -> None:
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "verify-signatures:" in release
    assert "python tooling/security/provenance_signature_gate.py --strict-key" in release
    assert "python tooling/security/policy_signature_gate.py --strict-key" in release
    assert "python tooling/security/slsa_attestation_gate.py" in release
    assert "python tooling/security/org_secret_backend_gate.py" in release
    assert "python tooling/security/secret_management_gate.py" in release
    assert "python tooling/security/production_controls_gate.py" in release
    assert "python tooling/security/third_party_pentest_gate.py --strict-key" in release
    assert "python tooling/security/live_rollout_gate.py" in release
    assert "python tooling/security/container_provenance_gate.py" in release
    assert "python tooling/security/container_registry_provenance_gate.py" in release
    assert "python tooling/security/attestation_digest_match_gate.py" in release
    assert "python tooling/security/stale_policy_review_gate.py" in release
    assert "python tooling/security/audit_archive_verify.py" in release
    assert "python tooling/security/abuse_telemetry_snapshot.py" in release
    assert "python tooling/security/abuse_telemetry_gate.py" in release
    assert "python tooling/security/exception_waiver_reconciliation_gate.py" in release
    assert "python tooling/security/promotion_policy_gate.py" in release
    assert "python tooling/security/evidence_attestation_index.py --strict-key" in release
    assert "python tooling/security/evidence_attestation_gate.py --strict-key" in release
    assert "python tooling/security/workflow_evidence_scope_gate.py" in release
    assert "python tooling/security/conformance_security_coupling_gate.py" in release
    assert "python tooling/security/security_super_gate.py --strict-key" in release
    assert "python tooling/security/live_rollout_gate.py --profile release" in release
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/release-build" in release
    assert "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/release-verify" in release
    assert "python tooling/security/evidence_run_dir_guard.py --run-id" in release
    assert 'GLYPHSER_CONTAINER_PUBLISHING_ENABLED: "true"' in release
    assert 'GLYPHSER_STRICT_SIGNING: "true"' in release
    assert "GLYPHSER_PROVENANCE_HMAC_KEY: ${{ secrets.GLYPHSER_PROVENANCE_HMAC_KEY }}" in release


def test_release_workflow_avoids_unpinned_action_tags() -> None:
    release = (ROOT / ".github" / "workflows" / "release.yml").read_text(encoding="utf-8")
    assert "actions/download-artifact@" not in release
    assert "gh-action-pypi-publish@" not in release
