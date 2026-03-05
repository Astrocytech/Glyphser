#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _enforce_allowed_write_root(path: Path) -> None:
    resolved = path.resolve()
    allowed = [((ROOT / "evidence").resolve()), Path("/tmp").resolve()]
    if any(_is_within(resolved, root) for root in allowed):
        return
    allowed_text = ", ".join(str(item) for item in allowed)
    raise ValueError(f"evidence run directory must be within allowed roots: {allowed_text}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ensure immutable run-scoped evidence directory.")
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args([] if argv is None else argv)

    root = evidence_root()
    _enforce_allowed_write_root(root)
    marker = root / ".run-marker.json"
    if marker.exists():
        raise ValueError(f"evidence run directory already initialized: {root}")
    root.mkdir(parents=True, exist_ok=True)
    marker.write_text(
        json.dumps({"run_id": args.run_id, "created_at_utc": datetime.now(UTC).isoformat()}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    print(f"EVIDENCE_RUN_DIR_GUARD: PASS ({root})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
