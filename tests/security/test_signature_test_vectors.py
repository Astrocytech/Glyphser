from __future__ import annotations

import json
from pathlib import Path

from runtime.glyphser.security import artifact_signing

VECTORS = Path(__file__).resolve().parents[1] / "fixtures" / "security" / "signature_test_vectors.json"


def _load_vectors() -> list[dict[str, str]]:
    payload = json.loads(VECTORS.read_text(encoding="utf-8"))
    return [item for item in payload.get("vectors", []) if isinstance(item, dict)]


def test_signature_vectors_signing_paths(monkeypatch, tmp_path: Path) -> None:
    for vector in _load_vectors():
        payload = str(vector["payload_utf8"]).encode("utf-8")
        expected = str(vector["expected_signature"])
        adapter = str(vector["adapter"])
        if adapter == "kms":
            monkeypatch.setenv("GLYPHSER_SIGNING_ADAPTER", "kms")
            monkeypatch.setenv("GLYPHSER_KMS_HMAC_KEY", str(vector["kms_key"]))
            got = artifact_signing.sign_bytes(payload, key=b"unused")
            assert got == expected, vector["id"]
            monkeypatch.delenv("GLYPHSER_KMS_HMAC_KEY", raising=False)
            monkeypatch.delenv("GLYPHSER_SIGNING_ADAPTER", raising=False)
            continue

        key = str(vector["key"]).encode("utf-8")
        monkeypatch.delenv("GLYPHSER_SIGNING_ADAPTER", raising=False)
        got = artifact_signing.sign_bytes(payload, key=key)
        assert got == expected, vector["id"]

        path = tmp_path / f"{vector['id']}.bin"
        path.write_bytes(payload)
        assert artifact_signing.sign_file(path, key=key) == expected
        assert artifact_signing.verify_file(path, expected, key=key)
        assert not artifact_signing.verify_file(path, "00" * 32, key=key)
