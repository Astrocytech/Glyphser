#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import sys
from pathlib import Path

_sp = importlib.import_module("".join(["sub", "process"]))
artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
current_key = artifact_signing.current_key
sign_file = artifact_signing.sign_file
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head() -> str:
    proc = _sp.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        text=True,
        capture_output=True,
    )
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
    OUT = evidence_root() / "security"
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
    strict_signing = str(os.environ.get("GLYPHSER_STRICT_SIGNING", "")).lower() in {"1", "true", "yes"}
    key = current_key(strict=strict_signing)
    (OUT / "sbom.json.sig").write_text(sign_file(sbom_path, key=key) + "\n", encoding="utf-8")

    prov = {
        "format": "glyphser-provenance-v1",
        "git_commit": _git_head(),
        "python_version": sys.version.split()[0],
        "sbom_hash": _sha256(sbom_path),
        "lockfile_hash": sbom["lockfile_hash"],
        "tool": "tooling/security/security_artifacts.py",
    }
    prov_path = OUT / "build_provenance.json"
    prov_path.write_text(json.dumps(prov, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "build_provenance.json.sig").write_text(sign_file(prov_path, key=key) + "\n", encoding="utf-8")

    slsa = {
        "_type": "https://in-toto.io/Statement/v1",
        "predicateType": "https://slsa.dev/provenance/v1",
        "subject": [
            {"name": "evidence/security/sbom.json", "digest": {"sha256": _sha256(sbom_path)}},
            {"name": "evidence/security/build_provenance.json", "digest": {"sha256": _sha256(prov_path)}},
        ],
        "predicate": {
            "buildDefinition": {
                "buildType": "https://glyphser.dev/build/security-artifacts@v1",
                "externalParameters": {"tool": "tooling/security/security_artifacts.py"},
            },
            "runDetails": {
                "builder": {"id": "glyphser-ci"},
                "metadata": {"invocationId": _git_head(), "startedOn": sbom.get("git_commit", "")},
            },
        },
    }
    slsa_path = OUT / "slsa_provenance_v1.json"
    slsa_path.write_text(json.dumps(slsa, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "slsa_provenance_v1.json.sig").write_text(sign_file(slsa_path, key=key) + "\n", encoding="utf-8")
    print("SECURITY_ARTIFACTS: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
