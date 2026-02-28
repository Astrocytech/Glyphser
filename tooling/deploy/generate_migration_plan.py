#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tooling.lib.path_config import generated_root

OUT_DIR = generated_root() / "deploy"
CATALOG_MANIFEST = ROOT / "specs" / "contracts" / "catalog-manifest.json"


def _read_manifest(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def generate(previous_manifest: Path | None = None) -> Path:
    current = _read_manifest(CATALOG_MANIFEST) if CATALOG_MANIFEST.exists() else {}
    previous = _read_manifest(previous_manifest) if previous_manifest and previous_manifest.exists() else {}

    plan = {
        "current_manifest": str(CATALOG_MANIFEST.relative_to(ROOT)).replace("\\", "/") if CATALOG_MANIFEST.exists() else "",
        "previous_manifest": str(previous_manifest.relative_to(ROOT)).replace("\\", "/") if previous_manifest else "",
        "actions": [],
        "rollback": [],
    }

    current_hash = current.get("derived_identities", {}).get("digest_catalog_hash")
    previous_hash = previous.get("derived_identities", {}).get("digest_catalog_hash") if previous else None

    if previous_hash and current_hash and previous_hash != current_hash:
        plan["actions"].append("Rebuild artifacts from new catalog digest")
        plan["rollback"].append("Restore prior catalog manifest and regenerate artifacts")
    else:
        plan["actions"].append("No schema digest changes detected")
        plan["rollback"].append("No rollback needed")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "migration_plan.json"
    out_path.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_path


def main() -> int:
    generate(None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
