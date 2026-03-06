from __future__ import annotations

import json
from pathlib import Path

from tooling.security import release_strict_key_mode_gate


def _write_release(repo: Path, text: str) -> None:
    wf = repo / ".github" / "workflows"
    wf.mkdir(parents=True, exist_ok=True)
    (wf / "release.yml").write_text(text, encoding="utf-8")


def test_release_strict_key_mode_gate_passes_when_all_signature_steps_use_strict_key(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_release(
        repo,
        "\n".join(
            [
                "jobs:",
                "  build:",
                "    steps:",
                "      - run: python tooling/security/policy_signature_generate.py --strict-key",
                "      - run: python tooling/security/policy_signature_gate.py --strict-key",
                "      - run: python tooling/security/provenance_signature_gate.py --strict-key",
                "      - run: python tooling/security/evidence_attestation_index.py --strict-key",
                "      - run: python tooling/security/evidence_attestation_gate.py --strict-key",
                "      - run: python tooling/security/security_super_gate.py --strict-key --strict-prereqs",
                "      - run: python tooling/security/third_party_pentest_gate.py --strict-key",
                "      - run: python tooling/security/formal_security_review_artifact.py --strict-key",
            ]
        )
        + "\n",
    )
    monkeypatch.setattr(release_strict_key_mode_gate, "ROOT", repo)
    monkeypatch.setattr(release_strict_key_mode_gate, "RELEASE_WORKFLOW", repo / ".github" / "workflows" / "release.yml")
    monkeypatch.setattr(release_strict_key_mode_gate, "evidence_root", lambda: repo / "evidence")
    assert release_strict_key_mode_gate.main([]) == 0


def test_release_strict_key_mode_gate_fails_when_any_signature_step_is_not_strict(
    monkeypatch, tmp_path: Path
) -> None:
    repo = tmp_path / "repo"
    _write_release(
        repo,
        "\n".join(
            [
                "jobs:",
                "  build:",
                "    steps:",
                "      - run: python tooling/security/policy_signature_generate.py --strict-key",
                "      - run: python tooling/security/policy_signature_gate.py --strict-key",
                "      - run: python tooling/security/provenance_signature_gate.py --strict-key",
                "      - run: python tooling/security/evidence_attestation_index.py --strict-key",
                "      - run: python tooling/security/evidence_attestation_gate.py",
                "      - run: python tooling/security/security_super_gate.py --strict-key --strict-prereqs",
                "      - run: python tooling/security/third_party_pentest_gate.py --strict-key",
                "      - run: python tooling/security/formal_security_review_artifact.py --strict-key",
            ]
        )
        + "\n",
    )
    monkeypatch.setattr(release_strict_key_mode_gate, "ROOT", repo)
    monkeypatch.setattr(release_strict_key_mode_gate, "RELEASE_WORKFLOW", repo / ".github" / "workflows" / "release.yml")
    monkeypatch.setattr(release_strict_key_mode_gate, "evidence_root", lambda: repo / "evidence")
    assert release_strict_key_mode_gate.main([]) == 1
    report = json.loads((repo / "evidence" / "security" / "release_strict_key_mode_gate.json").read_text(encoding="utf-8"))
    assert "signature_sensitive_step_missing_strict_key:evidence_attestation_gate.py" in report["findings"]
