from __future__ import annotations

import hashlib
import json
from pathlib import Path

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.security import offline_verify


def _canonical(payload: dict) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_offline_verify_passes_for_signed_bundle(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir(parents=True, exist_ok=True)
    sbom = bundle / "sbom.json"
    _write_json(sbom, {"status": "ok"})
    sbom.with_suffix(".json.sig").write_text(sign_file(sbom, key=current_key(strict=False)) + "\n", encoding="utf-8")

    chain = bundle / "evidence_chain_of_custody.json"
    rec = {"seq": 1, "path": "evidence/security/sbom.json", "sha256": "abc", "previous_hash": ""}
    digest = hashlib.sha256(_canonical(rec).encode("utf-8")).hexdigest()
    _write_json(chain, {"items": [{**rec, "digest": digest}]})
    chain.with_suffix(".json.sig").write_text(sign_file(chain, key=current_key(strict=False)) + "\n", encoding="utf-8")

    assert offline_verify.main(["--bundle-dir", str(bundle)]) == 0


def test_offline_verify_fails_on_chain_digest_mismatch(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir(parents=True, exist_ok=True)
    sbom = bundle / "sbom.json"
    _write_json(sbom, {"status": "ok"})
    sbom.with_suffix(".json.sig").write_text(sign_file(sbom, key=current_key(strict=False)) + "\n", encoding="utf-8")

    chain = bundle / "evidence_chain_of_custody.json"
    rec = {"seq": 1, "path": "evidence/security/sbom.json", "sha256": "abc", "previous_hash": "", "digest": "bad"}
    _write_json(chain, {"items": [rec]})
    chain.with_suffix(".json.sig").write_text(sign_file(chain, key=current_key(strict=False)) + "\n", encoding="utf-8")

    assert offline_verify.main(["--bundle-dir", str(bundle)]) == 1


def test_offline_verify_fails_on_invalid_non_json_signature(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir(parents=True, exist_ok=True)
    note = bundle / "audit_note.txt"
    note.write_text("offline evidence\n", encoding="utf-8")
    note.with_suffix(".txt.sig").write_text("invalid-signature\n", encoding="utf-8")

    assert offline_verify.main(["--bundle-dir", str(bundle)]) == 1


def test_offline_verify_fails_when_signature_payload_missing(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "orphan.json.sig").write_text("deadbeef\n", encoding="utf-8")

    assert offline_verify.main(["--bundle-dir", str(bundle)]) == 1
