#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = [
        ROOT / "conformance" / "results" / "latest.json",
        ROOT / "conformance" / "reports" / "latest.json",
        ROOT / "dist" / "hello-core-bundle.tar.gz",
        ROOT / "dist" / "hello-core-bundle.sha256",
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
