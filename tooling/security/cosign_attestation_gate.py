#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root


def main(argv: list[str] | None = None) -> int:
    _ = argv
    required = [
        ROOT / "distribution" / "container" / "image-digests.txt",
        ROOT / "distribution" / "container" / "image-digests.txt.sigstore",
    ]
    env_enabled = os.environ.get("GLYPHSER_CONTAINER_PUBLISHING_ENABLED", "").strip().lower()
    publishing_enabled = env_enabled in {"1", "true", "yes"}
    has_any_attestation = any(p.exists() for p in required)
    strict_mode = publishing_enabled or has_any_attestation
    missing = [str(p.relative_to(ROOT)).replace("\\", "/") for p in required if strict_mode and not p.exists()]
    report = {
        "status": "PASS" if not missing else "FAIL",
        "skipped": not strict_mode,
        "strict_mode": strict_mode,
        "findings": [f"missing_external_attestation:{m}" for m in missing],
        "summary": {"required_files": [str(p.relative_to(ROOT)).replace("\\", "/") for p in required]},
        "metadata": {"gate": "cosign_attestation_gate"},
    }
    out = evidence_root() / "security" / "cosign_attestation_gate.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"COSIGN_ATTESTATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
