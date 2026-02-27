from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


ARTIFACT_PATHS = [
    ROOT / "contracts" / "catalog-manifest.json",
    ROOT / "fixtures" / "hello-core" / "fixture-manifest.json",
    ROOT / "fixtures" / "hello-core" / "manifest.core.yaml",
    ROOT / "goldens" / "hello-core" / "golden-manifest.json",
    ROOT / "goldens" / "hello-core" / "golden-identities.json",
    ROOT / "goldens" / "hello-core" / "trace_snippet.json",
    ROOT / "vectors" / "hello-core" / "vectors-manifest.json",
    ROOT / "vectors" / "hello-core" / "vectors.json",
]


def sha256_hex(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_materialize() -> str:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "materialize_doc_artifacts.py")],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def run_verify() -> str:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "verify_doc_artifacts.py")],
        cwd=str(ROOT),
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.strip()


def snapshot_hashes() -> dict[str, str]:
    missing = [str(p) for p in ARTIFACT_PATHS if not p.exists()]
    assert not missing, f"missing artifacts: {missing}"
    return {str(p.relative_to(ROOT)): sha256_hex(p) for p in ARTIFACT_PATHS}


def test_materialize_and_verify_repeatable():
    run_materialize()
    first_hashes = snapshot_hashes()
    first_verify = run_verify()

    run_materialize()
    second_hashes = snapshot_hashes()
    second_verify = run_verify()

    assert first_hashes == second_hashes
    assert first_verify == second_verify
