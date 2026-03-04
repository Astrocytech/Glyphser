#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root

REQUIRED = [
    ROOT / "distribution" / "container" / "image-digests.txt",
    ROOT / "distribution" / "container" / "image-digests.txt.sigstore",
]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    missing = [str(p.relative_to(ROOT)).replace("\\", "/") for p in REQUIRED if not p.exists()]
    report = {
        "status": "PASS" if not missing else "FAIL",
        "findings": [f"missing_external_attestation:{m}" for m in missing],
        "summary": {"required_files": [str(p.relative_to(ROOT)).replace("\\", "/") for p in REQUIRED]},
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
