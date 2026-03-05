from __future__ import annotations

import hashlib
import hmac

import pytest

from runtime.glyphser.security import artifact_signing


def test_current_key_allows_fallback_by_default(monkeypatch) -> None:
    monkeypatch.delenv("GLYPHSER_PROVENANCE_HMAC_KEY", raising=False)
    monkeypatch.delenv("GLYPHSER_ENV", raising=False)
    key = artifact_signing.current_key(strict=False)
    assert key


def test_current_key_requires_key_in_non_local_mode(monkeypatch) -> None:
    monkeypatch.delenv("GLYPHSER_PROVENANCE_HMAC_KEY", raising=False)
    monkeypatch.setenv("GLYPHSER_ENV", "ci")
    with pytest.raises(ValueError, match="missing required signing key env"):
        artifact_signing.current_key(strict=False)


def test_key_metadata_reports_source(monkeypatch) -> None:
    monkeypatch.setenv("GLYPHSER_PROVENANCE_HMAC_KEY", "k")
    meta = artifact_signing.key_metadata(strict=True)
    assert meta["source"] == "env"
    assert meta["fallback_used"] is False


def test_kms_adapter_requires_key(monkeypatch) -> None:
    monkeypatch.setenv("GLYPHSER_SIGNING_ADAPTER", "kms")
    monkeypatch.delenv("GLYPHSER_KMS_HMAC_KEY", raising=False)
    with pytest.raises(ValueError, match="missing required KMS adapter key env"):
        artifact_signing.sign_bytes(b"abc", key=b"unused")


def test_hmac_signing_zeroizes_temporary_key_buffer(monkeypatch) -> None:
    monkeypatch.delenv("GLYPHSER_SIGNING_ADAPTER", raising=False)
    snapshots: list[bytes] = []
    original = artifact_signing.zeroize_bytearray

    def _spy(buf: bytearray) -> None:
        snapshots.append(bytes(buf))
        original(buf)
        snapshots.append(bytes(buf))

    monkeypatch.setattr(artifact_signing, "zeroize_bytearray", _spy)
    key = b"unit-test-signing-key"
    payload = b"abc"
    got = artifact_signing.sign_bytes(payload, key=key)
    expected = hmac.new(key, payload, hashlib.sha256).hexdigest()
    assert got == expected
    assert snapshots == [key, b"\x00" * len(key)]
