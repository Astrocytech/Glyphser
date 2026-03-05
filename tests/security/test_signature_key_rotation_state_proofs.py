from __future__ import annotations

from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import policy_signature_gate, security_toolchain_lock_signature_gate


def _reset_signing_env(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    for key in (
        "GLYPHSER_PROVENANCE_HMAC_KEY",
        "GLYPHSER_REQUIRE_SIGNING_KEY",
        "GLYPHSER_ENV",
        "GLYPHSER_SIGNING_ADAPTER",
    ):
        monkeypatch.delenv(key, raising=False)


def test_signature_verification_key_rotation_state_machine_is_deterministic(
    monkeypatch, tmp_path: Path
) -> None:
    _reset_signing_env(monkeypatch)
    payload = tmp_path / "policy.json"
    payload.write_text('{"k":"v"}\n', encoding="utf-8")

    # State A: bootstrap/fallback signature.
    bootstrap_sig = sign_file(payload, key=current_key(strict=False))

    # State B: rotated strict key signature.
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "rotated-signing-key-v2")
    rotated_sig = sign_file(payload, key=current_key(strict=True))

    # State C: invalid signature.
    invalid_sig = "deadbeef"

    # Verify repeated runs stay deterministic for each state.
    scenarios = [
        ("S1", False, None, bootstrap_sig, (True, "ok")),
        ("S2", True, "rotated-signing-key-v2", rotated_sig, (True, "ok")),
        ("S3", True, "rotated-signing-key-v2", bootstrap_sig, (True, "ok_bootstrap_key")),
        ("S4", True, None, bootstrap_sig, (True, "ok_bootstrap_key_missing_strict_env")),
        ("S5", True, None, invalid_sig, (False, "missing required signing key env: GLYPHSER_PROVENANCE_HMAC_KEY")),
    ]

    for _name, strict_key, env_key, signature, expected in scenarios:
        results_policy: list[tuple[bool, str]] = []
        results_toolchain: list[tuple[bool, str]] = []
        for _ in range(5):
            _reset_signing_env(monkeypatch)
            if env_key is not None:
                monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", env_key)
            policy_tuple = policy_signature_gate._verify_with_allowed_keys(
                payload, signature, strict_key=strict_key
            )
            toolchain_tuple = security_toolchain_lock_signature_gate._verify_with_allowed_keys(
                payload, signature, strict_key=strict_key
            )
            results_policy.append(policy_tuple)
            results_toolchain.append(toolchain_tuple)

        assert all(item == expected for item in results_policy)
        assert all(item == expected for item in results_toolchain)
