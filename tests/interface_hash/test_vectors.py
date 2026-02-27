from __future__ import annotations

import json
from pathlib import Path

from src.glyphser.registry.interface_hash import compute_interface_hash
from tools import materialize_doc_artifacts as mda

ROOT = Path(__file__).resolve().parents[1]
VECTORS = ROOT / "conformance" / "vectors" / "interface_hash" / "vectors.json"


def test_interface_hash_vectors():
    data = json.loads(VECTORS.read_text(encoding="utf-8"))
    catalogs = mda.build_catalogs()
    registry = mda.build_operator_registry(catalogs["digest_map"])
    actual = compute_interface_hash(registry)
    expected = data["vectors"][0]["expected_interface_hash"]
    assert actual == expected
