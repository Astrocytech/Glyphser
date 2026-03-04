#!/usr/bin/env python3
from __future__ import annotations

import argparse
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate signatures for governance security policy files.")
    parser.add_argument("--strict-key", action="store_true", help="Require explicit signing key env.")
    args = parser.parse_args([] if argv is None else argv)

    manifest_path = ROOT / "governance" / "security" / "policy_signature_manifest.json"
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    files = []
    if isinstance(payload, dict):
        raw = payload.get("files", payload.get("policies", []))
        if isinstance(raw, list):
            files = raw
    if not isinstance(files, list):
        raise ValueError("policy signature manifest must contain list 'files'")

    key = current_key(strict=args.strict_key)
    count = 0
    for rel in files:
        if not isinstance(rel, str) or not rel.strip():
            continue
        path = ROOT / rel
        if not path.exists():
            raise ValueError(f"missing policy file: {rel}")
        sig_path = path.with_suffix(path.suffix + ".sig")
        sig_path.write_text(sign_file(path, key=key) + "\n", encoding="utf-8")
        count += 1
    print(f"POLICY_SIGNATURE_GENERATE: signed {count} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
