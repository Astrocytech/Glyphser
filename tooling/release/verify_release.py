#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHECKSUM_FILE = ROOT / "distribution" / "release" / "CHECKSUMS_v0.1.0.sha256"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while True:
            chunk = fh.read(1024 * 1024)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def _load_expected(path: Path) -> list[tuple[str, Path]]:
    entries: list[tuple[str, Path]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split(maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"Invalid checksum line: {line!r}")
        digest, rel = parts
        entries.append((digest, ROOT / rel.strip()))
    return entries


def main() -> int:
    if not CHECKSUM_FILE.exists():
        print(f"missing checksum file: {CHECKSUM_FILE}")
        return 1

    print("STEP 1: running push-button pipeline")
    rc = subprocess.run([sys.executable, "tooling/commands/push_button.py"], cwd=ROOT).returncode
    if rc != 0:
        return rc

    print("STEP 2: verifying release checksums")
    try:
        expected = _load_expected(CHECKSUM_FILE)
    except ValueError as exc:
        print(str(exc))
        return 1

    status = 0
    for want, path in expected:
        rel = path.relative_to(ROOT).as_posix()
        if not path.exists():
            print(f"FAIL missing: {rel}")
            status = 1
            continue
        got = _sha256(path)
        if got != want:
            print(f"FAIL hash mismatch: {rel}")
            print(f"  expected: {want}")
            print(f"  actual:   {got}")
            status = 1
        else:
            print(f"OK {rel}")

    if status == 0:
        print("VERIFY_RELEASE: PASS")
    return status


if __name__ == "__main__":
    raise SystemExit(main())
