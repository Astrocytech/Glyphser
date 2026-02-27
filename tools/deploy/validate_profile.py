#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEPLOY_DIR = ROOT / "generated" / "deploy"


REQUIRED_FILES = ["runtime_config.json", "policy_bindings.json", "bundle_manifest.json"]


def validate(profile: str) -> int:
    profile = profile.lower()
    if profile not in {"managed", "confidential", "regulated"}:
        print("invalid profile")
        return 1

    base = DEPLOY_DIR / profile
    missing = [name for name in REQUIRED_FILES if not (base / name).exists()]
    if missing:
        print(f"missing files for {profile}: {missing}")
        return 1

    manifest = json.loads((base / "bundle_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("profile") != profile:
        print("profile mismatch in manifest")
        return 1

    return 0


def main() -> int:
    status = 0
    for profile in ("managed", "confidential", "regulated"):
        status |= validate(profile)
    return status


if __name__ == "__main__":
    raise SystemExit(main())
