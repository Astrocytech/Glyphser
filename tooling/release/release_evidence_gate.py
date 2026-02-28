#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tooling.path_config import bundles_root, conformance_reports_root, conformance_results_root


def main() -> int:
    bundles = bundles_root()
    required = [
        conformance_results_root() / "latest.json",
        conformance_reports_root() / "latest.json",
        bundles / "hello-core-bundle.tar.gz",
        bundles / "hello-core-bundle.sha256",
    ]

    missing = [str(p) for p in required if not p.exists()]
    if missing:
        print("RELEASE_EVIDENCE_GATE: FAIL")
        for p in missing:
            print(f" - missing: {p}")
        return 1

    print("RELEASE_EVIDENCE_GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
