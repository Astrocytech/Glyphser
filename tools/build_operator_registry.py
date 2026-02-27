#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tools import materialize_doc_artifacts as mda  # noqa: E402
from src.glyphser.registry.interface_hash import compute_interface_hash  # noqa: E402
from src.glyphser.registry.registry_builder import (  # noqa: E402
    build_operator_registry_from_list,
    parse_api_interfaces,
)


def _jsonify(obj: Any) -> Any:
    if isinstance(obj, bytes):
        return f"hex:{obj.hex()}"
    if isinstance(obj, dict):
        return {k: _jsonify(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_jsonify(v) for v in obj]
    return obj


def main() -> int:
    catalogs = mda.build_catalogs()

    api_path = ROOT / "docs" / "layer1-foundation" / "API-Interfaces.md"
    api_ops = parse_api_interfaces(api_path)

    registry = build_operator_registry_from_list(api_ops, catalogs["digest_map"])

    contracts_dir = ROOT / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)

    src_path = contracts_dir / "operator_registry_source.json"
    src_path.write_text(
        json.dumps({"source": str(api_path), "operators": api_ops}, indent=2, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )

    json_path = contracts_dir / "operator_registry.json"
    json_path.write_text(
        json.dumps(_jsonify(registry), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    cbor_path = contracts_dir / "operator_registry.cbor"
    cbor_path.write_bytes(mda.cbor_encode(registry))

    interface_hash = compute_interface_hash(registry)
    hash_path = contracts_dir / "interface_hash.json"
    hash_path.write_text(
        json.dumps({"interface_hash": interface_hash}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("Glyphser operator registry: OK")
    print(f"registry_json: {json_path}")
    print(f"registry_cbor: {cbor_path}")
    print(f"registry_source: {src_path}")
    print(f"interface_hash: {interface_hash}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
