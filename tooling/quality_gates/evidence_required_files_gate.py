#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED = {
    "summary.md",
    "env-matrix.json",
    "conformance-hashes.json",
    "repro-classification.json",
    "known-limitations.md",
    "milestone.json",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate required milestone evidence files exist.")
    parser.add_argument(
        "--milestone-dir",
        required=True,
        help="Path to evidence/repro/milestone-*/ directory.",
    )
    parser.add_argument("--report", default="", help="Optional JSON report path.")
    args = parser.parse_args()

    root = Path(args.milestone_dir)
    missing = sorted([name for name in REQUIRED if not (root / name).exists()])
    payload = {
        "milestone_dir": str(root),
        "required_count": len(REQUIRED),
        "missing": missing,
        "status": "PASS" if not missing else "FAIL",
    }
    if args.report:
        rp = Path(args.report)
        rp.parent.mkdir(parents=True, exist_ok=True)
        rp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if not missing else 1


if __name__ == "__main__":
    raise SystemExit(main())
