#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from tooling.lib.path_config import evidence_root
from tooling.security.stage_s_policy import load_stage_s_policy

ROOT = Path(__file__).resolve().parents[2]


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _merkle_root(leaves: list[str]) -> str:
    if not leaves:
        return hashlib.sha256(b"").hexdigest()
    layer = [bytes.fromhex(h) for h in leaves]
    while len(layer) > 1:
        nxt: list[bytes] = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i + 1] if i + 1 < len(layer) else layer[i]
            nxt.append(hashlib.sha256(a + b).digest())
        layer = nxt
    return layer[0].hex()


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cfg = load_stage_s_policy().get("transparency_log", {})
    log_path = ROOT / str(cfg.get("log_path", "evidence/security/transparency_log.json"))
    tracked = [ROOT / str(p) for p in cfg.get("tracked_paths", []) if isinstance(p, str)]

    entries: list[dict[str, object]] = []
    if log_path.exists():
        existing = json.loads(log_path.read_text(encoding="utf-8"))
        if isinstance(existing, dict) and isinstance(existing.get("entries"), list):
            entries = [e for e in existing.get("entries", []) if isinstance(e, dict)]

    leaves: list[str] = []
    tracked_hashes: dict[str, str] = {}
    for path in tracked:
        if path.exists():
            digest = _sha(path)
            tracked_hashes[str(path.relative_to(ROOT)).replace("\\", "/")] = digest
            leaves.append(digest)

    root = _merkle_root(leaves)
    prev_root = str(entries[-1].get("root", "")) if entries else ""
    entries.append(
        {
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "previous_root": prev_root,
            "root": root,
            "tracked_hashes": tracked_hashes,
        }
    )
    payload = {"entries": entries}
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    report = {
        "status": "PASS",
        "findings": [],
        "summary": {"entries": len(entries), "latest_root": root},
        "metadata": {"tool": "transparency_log_export"},
    }
    out = evidence_root() / "security" / "transparency_log_export.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("TRANSPARENCY_LOG_EXPORT: PASS")
    print(f"Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
