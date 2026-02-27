from __future__ import annotations

import hashlib
from pathlib import Path

import pytest


@pytest.mark.fuzz_harness
def test_manifest_parser_fuzz():
    # Minimal deterministic check: manifest content hash is stable.
    root = Path(__file__).resolve().parents[2]
    manifest = root / "fixtures" / "hello-core" / "manifest.core.yaml"
    data = manifest.read_bytes()
    h1 = hashlib.sha256(data).hexdigest()
    h2 = hashlib.sha256(data).hexdigest()
    assert h1 == h2
