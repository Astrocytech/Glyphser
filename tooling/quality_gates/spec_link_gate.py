#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import List

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "governance" / "structure" / "spec_link_policy.json"
OUT = ROOT / "evidence" / "gates" / "structure" / "spec_link_gate.json"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _load_config() -> dict:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def evaluate() -> dict:
    cfg = _load_config()
    required_globs = cfg.get("required_globs", [])
    markers = cfg.get("reference_markers", ["specs/", "specs/schemas/"])

    targets: List[Path] = []
    for pattern in required_globs:
        targets.extend(sorted(ROOT.glob(pattern)))
    # de-duplicate while preserving deterministic order
    unique_targets = []
    seen = set()
    for p in targets:
        key = str(p.resolve())
        if key not in seen and p.is_file():
            seen.add(key)
            unique_targets.append(p)

    violations = []
    for path in unique_targets:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if not any(marker in text for marker in markers):
            violations.append(_rel(path))

    payload = {
        "status": "PASS" if not violations else "FAIL",
        "checked_files": [_rel(p) for p in unique_targets],
        "missing_spec_links": violations,
        "markers": markers,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return payload


def main() -> int:
    report = evaluate()
    if report["status"] != "PASS":
        print("SPEC_LINK_GATE: FAIL")
        return 1
    print("SPEC_LINK_GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
