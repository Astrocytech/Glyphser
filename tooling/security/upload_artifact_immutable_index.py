#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
verify_file = artifact_signing.verify_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _collect_files() -> list[Path]:
    files: list[Path] = []
    dist = ROOT / "dist"
    if dist.exists():
        for path in dist.rglob("*"):
            if path.is_file():
                files.append(path)

    sec = evidence_root() / "security"
    if sec.exists():
        ignored = {"upload_artifact_immutable_index.json", "upload_artifact_immutable_index.json.sig"}
        for path in sec.rglob("*"):
            if not path.is_file():
                continue
            if path.name in ignored:
                continue
            files.append(path)

    return sorted(set(files), key=lambda p: str(p.relative_to(ROOT)).replace("\\", "/"))


def _index_root(items: list[dict[str, Any]]) -> str:
    rolling = "0" * 64
    for item in items:
        record = f"{rolling}|{item['path']}|{item['size_bytes']}|{item['sha256']}".encode("utf-8")
        rolling = _sha256_bytes(record)
    return rolling


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    findings: list[str] = []
    files = _collect_files()
    if not files:
        findings.append("missing_upload_artifacts")

    items: list[dict[str, Any]] = []
    for path in files:
        items.append(
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "size_bytes": path.stat().st_size,
                "sha256": _sha256_file(path),
            }
        )

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "artifact_count": len(items),
            "index_root": _index_root(items),
            "immutable": True,
        },
        "metadata": {"gate": "upload_artifact_immutable_index", "omission_attack_detection": True},
        "items": items,
    }

    out = sec / "upload_artifact_immutable_index.json"
    write_json_report(out, payload)
    sig_path = out.with_suffix(".json.sig")
    sig_path.write_text(sign_file(out, key=current_key(strict=False)) + "\n", encoding="utf-8")
    signature = sig_path.read_text(encoding="utf-8").strip()
    if not verify_file(out, signature, key=current_key(strict=False)):
        findings.append("upload_artifact_immutable_index_signature_invalid")
        payload["status"] = "FAIL"
        payload["findings"] = findings
        write_json_report(out, payload)

    print(f"UPLOAD_ARTIFACT_IMMUTABLE_INDEX: {payload['status']}")
    print(f"Index: {out}")
    print(f"Signature: {sig_path}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
