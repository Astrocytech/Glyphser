#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import os
import re
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

_HEX_256 = re.compile(r"^[0-9a-f]{64}$")


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def _security_files(sec: Path) -> list[Path]:
    ignored = {
        "rolling_merkle_checkpoints.json",
        "rolling_merkle_checkpoints.json.sig",
        "rolling_merkle_checkpoints_gate.json",
    }
    files: list[Path] = []
    for path in sec.rglob("*"):
        if not path.is_file():
            continue
        if path.name in ignored:
            continue
        if path.name.endswith(".sig"):
            continue
        files.append(path)
    return sorted(files, key=lambda item: str(item.relative_to(sec)).replace("\\", "/"))


def _rolling_checkpoint(previous_root: str, rel_path: str, leaf_sha256: str) -> str:
    seed = f"{previous_root}|{rel_path}|{leaf_sha256}".encode("utf-8")
    return _sha256_bytes(seed)


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)

    findings: list[str] = []
    previous_root = os.environ.get("GLYPHSER_MERKLE_PREVIOUS_ROOT", "").strip().lower()
    if previous_root and not _HEX_256.fullmatch(previous_root):
        findings.append("invalid_previous_root_hex")

    stage = os.environ.get("GLYPHSER_MERKLE_STAGE", "").strip()
    if not stage:
        stage = evidence_root().name or "security"

    files = _security_files(sec)
    if not files:
        findings.append("missing_security_artifacts")

    checkpoints: list[dict[str, Any]] = []
    rolling = previous_root if _HEX_256.fullmatch(previous_root) else "0" * 64
    for idx, path in enumerate(files, start=1):
        rel_path = str(path.relative_to(ROOT)).replace("\\", "/")
        leaf_sha = _sha256_file(path)
        rolling = _rolling_checkpoint(rolling, rel_path, leaf_sha)
        checkpoints.append(
            {
                "index": idx,
                "path": rel_path,
                "sha256": leaf_sha,
                "rolling_root": rolling,
            }
        )

    payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "stage": stage,
            "artifact_count": len(files),
            "previous_root": previous_root,
            "final_root": rolling,
        },
        "metadata": {"gate": "rolling_merkle_checkpoints", "run_scoped_artifacts": True},
        "checkpoints": checkpoints,
    }

    out = sec / "rolling_merkle_checkpoints.json"
    write_json_report(out, payload)
    sig_path = out.with_suffix(".json.sig")
    sig_path.write_text(sign_file(out, key=current_key(strict=False)) + "\n", encoding="utf-8")
    signature = sig_path.read_text(encoding="utf-8").strip()
    if not verify_file(out, signature, key=current_key(strict=False)):
        findings.append("rolling_merkle_checkpoints_signature_invalid")
        payload["status"] = "FAIL"
        payload["findings"] = findings
        write_json_report(out, payload)

    gate = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "stage": stage,
            "artifact_count": len(files),
            "previous_root": previous_root,
            "final_root": payload["summary"]["final_root"],
        },
        "metadata": {"gate": "rolling_merkle_checkpoints_gate"},
    }
    gate_path = sec / "rolling_merkle_checkpoints_gate.json"
    write_json_report(gate_path, gate)
    print(f"ROLLING_MERKLE_CHECKPOINTS: {gate['status']}")
    print(f"Checkpoint: {out}")
    print(f"Gate: {gate_path}")
    return 0 if gate["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
