#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "evidence"
ARCHIVE = EVIDENCE / "archive"

ARCHIVE_TARGETS = [
    "benchmarks/latest.json",
    "benchmarks/variance_impact.json",
    "security/sbom.json",
    "security/build_provenance.json",
    "traceability/index.json",
    "metadata/catalog.json",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def archive(root: Path = ROOT, keep: int = 10) -> dict:
    evidence = root / "evidence"
    archive_root = evidence / "archive"
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    target_dir = archive_root / stamp
    target_dir.mkdir(parents=True, exist_ok=True)

    archived_files = []
    for rel in ARCHIVE_TARGETS:
        src = evidence / rel
        if not src.exists():
            continue
        dst = target_dir / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        archived_files.append({"path": rel, "sha256": _sha256(dst)})

    snapshot = {
        "snapshot_id": stamp,
        "created_at_utc": datetime.now(UTC).isoformat(),
        "file_count": len(archived_files),
        "files": archived_files,
    }

    index_path = archive_root / "index.json"
    index = {"schema_version": "glyphser-evidence-archive-index.v1", "snapshots": []}
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding="utf-8"))
    snapshots = index.get("snapshots", [])
    snapshots.append(snapshot)
    snapshots = sorted(snapshots, key=lambda x: x["snapshot_id"])

    while len(snapshots) > keep:
        old = snapshots.pop(0)
        old_dir = archive_root / old["snapshot_id"]
        if old_dir.exists():
            shutil.rmtree(old_dir)

    index["snapshots"] = snapshots
    archive_root.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return snapshot


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive and retain evidence snapshots")
    parser.add_argument("--keep", type=int, default=10)
    args = parser.parse_args()
    snap = archive(ROOT, keep=args.keep)
    print(json.dumps(snap, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
