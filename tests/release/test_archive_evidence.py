from __future__ import annotations

import json
from pathlib import Path

from tooling.release.archive_evidence import archive


def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_archive_evidence_retention(tmp_path: Path):
    root = tmp_path
    evidence = root / "evidence"

    _write_json(evidence / "benchmarks" / "latest.json", {"x": 1})
    _write_json(evidence / "benchmarks" / "variance_impact.json", {"x": 2})
    _write_json(evidence / "security" / "sbom.json", {"x": 3})
    _write_json(evidence / "security" / "build_provenance.json", {"x": 4})
    _write_json(evidence / "traceability" / "index.json", {"x": 5})
    _write_json(evidence / "metadata" / "catalog.json", {"x": 6})

    archive(root, keep=2)
    archive(root, keep=2)
    archive(root, keep=2)

    index = json.loads((evidence / "archive" / "index.json").read_text(encoding="utf-8"))
    assert len(index["snapshots"]) <= 2
