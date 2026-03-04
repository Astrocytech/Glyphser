#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.glyphser.security.artifact_signing import current_key, sign_file
from tooling.lib.path_config import evidence_root


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build signed security evidence attestation index.")
    parser.add_argument("--strict-key", action="store_true", help="Require GLYPHSER_PROVENANCE_HMAC_KEY.")
    args = parser.parse_args([] if argv is None else argv)

    sec = evidence_root() / "security"
    sec.mkdir(parents=True, exist_ok=True)
    files = sorted(
        p
        for p in sec.glob("*")
        if p.is_file()
        and p.name not in {"evidence_attestation_index.json", "evidence_attestation_index.json.sig"}
        and not p.name.endswith(".sig")
    )
    items = [
        {"path": str(p.relative_to(ROOT)).replace("\\", "/"), "sha256": _sha256_file(p)}
        for p in files
    ]
    payload = {
        "status": "PASS",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "count": len(items),
        "items": items,
    }
    index_path = sec / "evidence_attestation_index.json"
    index_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    sig_path = sec / "evidence_attestation_index.json.sig"
    sig_path.write_text(sign_file(index_path, key=current_key(strict=args.strict_key)) + "\n", encoding="utf-8")
    print(f"EVIDENCE_ATTESTATION_INDEX: {index_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
