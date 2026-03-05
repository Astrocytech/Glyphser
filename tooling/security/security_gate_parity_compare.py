#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _load(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"invalid snapshot format: {path}")
    return payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Compare cross-version security gate parity snapshots.")
    parser.add_argument("--left", required=True, help="Path to first parity snapshot JSON.")
    parser.add_argument("--right", required=True, help="Path to second parity snapshot JSON.")
    args = parser.parse_args([] if argv is None else argv)

    left = _load(Path(args.left))
    right = _load(Path(args.right))

    left_hash = str(left.get("parity_hash", "")).strip()
    right_hash = str(right.get("parity_hash", "")).strip()
    if not left_hash or not right_hash:
        print("SECURITY_GATE_PARITY_COMPARE: FAIL (missing parity hash)")
        return 1
    if left_hash != right_hash:
        print("SECURITY_GATE_PARITY_COMPARE: FAIL (parity hash mismatch)")
        print(f"left={left_hash}")
        print(f"right={right_hash}")
        return 1

    print("SECURITY_GATE_PARITY_COMPARE: PASS")
    print(f"parity_hash={left_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
