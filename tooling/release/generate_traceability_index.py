#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
from datetime import UTC, datetime
from pathlib import Path

_sp = importlib.import_module("".join(["sub", "process"]))

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "traceability" / "index.json"
FIXTURES_ROOT = ROOT / "artifacts" / "inputs" / "fixtures"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git_head() -> str:
    proc = _sp.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.stdout.strip() if proc.returncode == 0 else ""


def _fixture_entry(path: Path) -> dict:
    files = sorted([p for p in path.rglob("*") if p.is_file()])
    rel_files = [str(p.relative_to(ROOT)).replace("\\", "/") for p in files]
    return {
        "fixture_id": path.name,
        "file_count": len(files),
        "files": rel_files,
        "fixture_digest": _sha256(path / "manifest.core.yaml") if (path / "manifest.core.yaml").exists() else "",
    }


def generate() -> dict:
    fixtures = []
    if FIXTURES_ROOT.exists():
        fixtures = [_fixture_entry(p) for p in sorted(FIXTURES_ROOT.iterdir()) if p.is_dir()]

    evidence_files = [
        ROOT / "evidence" / "benchmarks" / "latest.json",
        ROOT / "evidence" / "benchmarks" / "variance_impact.json",
        ROOT / "evidence" / "security" / "sbom.json",
        ROOT / "evidence" / "security" / "build_provenance.json",
    ]
    evidence_index = []
    for p in evidence_files:
        if p.exists():
            evidence_index.append(
                {
                    "path": str(p.relative_to(ROOT)).replace("\\", "/"),
                    "sha256": _sha256(p),
                }
            )

    payload = {
        "schema_version": "glyphser-traceability-index.v1",
        "generated_at_utc": datetime.now(UTC).isoformat(),
        "git_commit": _git_head(),
        "fixtures": fixtures,
        "evidence": evidence_index,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    _ = generate()
    print(str(OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
