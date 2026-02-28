#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tooling"))
from path_config import evidence_root

OUT = evidence_root() / "security"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head() -> str:
    proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=False, text=True, capture_output=True)
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _load_lock_packages(path: Path) -> list[dict]:
    out: list[dict] = []
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "==" not in line:
            continue
        name, version = line.split("==", 1)
        out.append({"name": name, "version": version})
    return sorted(out, key=lambda x: (x["name"], x["version"]))


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    lock = ROOT / "requirements.lock"
    pyproject = ROOT / "pyproject.toml"
    sbom = {
        "format": "glyphser-sbom-v1",
        "git_commit": _git_head(),
        "lockfile_hash": _sha256(lock) if lock.exists() else "",
        "pyproject_hash": _sha256(pyproject) if pyproject.exists() else "",
        "packages": _load_lock_packages(lock),
    }
    sbom_path = OUT / "sbom.json"
    sbom_path.write_text(json.dumps(sbom, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    prov = {
        "format": "glyphser-provenance-v1",
        "git_commit": _git_head(),
        "python_version": sys.version.split()[0],
        "sbom_hash": _sha256(sbom_path),
        "lockfile_hash": sbom["lockfile_hash"],
        "tool": "tooling/security_artifacts.py",
    }
    prov_path = OUT / "build_provenance.json"
    prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("SECURITY_ARTIFACTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
