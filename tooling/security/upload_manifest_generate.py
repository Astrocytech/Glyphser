#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def _artifact_list(sec: Path) -> list[str]:
    out: list[str] = []
    for path in sorted(sec.glob("*")):
        if not path.is_file():
            continue
        out.append(path.name)
    return out


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    manifest_path = sec / "upload_manifest.json"
    sig_path = sec / "upload_manifest.json.sig"
    artifacts = _artifact_list(sec)
    payload = {
        "status": "PASS",
        "findings": [],
        "summary": {"artifact_count": len(artifacts), "artifacts": artifacts},
        "metadata": {"gate": "upload_manifest_generate"},
    }
    write_json_report(manifest_path, payload)
    sig_path.write_text(sign_file(manifest_path, key=current_key(strict=False)) + "\n", encoding="utf-8")
    print(f"UPLOAD_MANIFEST_GENERATE: {manifest_path}")
    print(f"Signature: {sig_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
