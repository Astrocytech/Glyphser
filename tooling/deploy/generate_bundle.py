#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Dict, List
import sys

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "tooling" / "deploy" / "templates"
sys.path.insert(0, str(ROOT))
from tooling.lib.path_config import generated_root

OUT_DIR = generated_root() / "deploy"
CATALOG_MANIFEST = ROOT / "specs" / "contracts" / "catalog-manifest.json"


def _sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _render(template_name: str, **values: str) -> str:
    template = (TEMPLATES / template_name).read_text(encoding="utf-8")
    return template.format(**values)


def _write_json(path: Path, payload: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _bundle_hash(entries: List[Dict[str, str]]) -> str:
    payload = json.dumps(entries, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return _sha256_hex(payload)


def generate(profile: str) -> Path:
    profile = profile.lower()
    if profile not in {"managed", "confidential", "regulated"}:
        raise ValueError("profile must be managed, confidential, or regulated")

    execution_mode = profile
    storage_root = f"data/{profile}"
    artifact_root = f"artifacts/{profile}"

    runtime_text = _render(
        "runtime_config.json.tpl",
        profile=profile,
        execution_mode=execution_mode,
        storage_root=storage_root,
        artifact_root=artifact_root,
    )
    policy_text = _render("policy_bindings.json.tpl", profile=profile)

    bundle_dir = OUT_DIR / profile
    bundle_dir.mkdir(parents=True, exist_ok=True)

    runtime_path = bundle_dir / "runtime_config.json"
    policy_path = bundle_dir / "policy_bindings.json"
    runtime_path.write_text(runtime_text + "\n", encoding="utf-8")
    policy_path.write_text(policy_text + "\n", encoding="utf-8")

    catalog_hash = ""
    if CATALOG_MANIFEST.exists():
        catalog_hash = json.loads(CATALOG_MANIFEST.read_text(encoding="utf-8")).get(
            "derived_identities", {}
        ).get("digest_catalog_hash", "")

    entries = [
        {"path": str(runtime_path.relative_to(ROOT)).replace("\\", "/"), "sha256": _sha256_hex(runtime_path.read_bytes())},
        {"path": str(policy_path.relative_to(ROOT)).replace("\\", "/"), "sha256": _sha256_hex(policy_path.read_bytes())},
    ]
    manifest = {
        "profile": profile,
        "catalog_digest": catalog_hash,
        "bundle_hash": _bundle_hash(entries),
        "artifacts": entries,
    }
    _write_json(bundle_dir / "bundle_manifest.json", manifest)
    return bundle_dir


def main() -> int:
    for profile in ("managed", "confidential", "regulated"):
        generate(profile)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
