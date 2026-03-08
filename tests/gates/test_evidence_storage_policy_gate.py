from __future__ import annotations

import json
from pathlib import Path

from tooling.quality_gates import evidence_storage_policy_gate


def _write_json(path: Path, payload: dict):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_evidence_storage_policy_gate_passes_with_clean_tracked_set(tmp_path: Path):
    root = tmp_path
    _write_json(
        root / "governance" / "structure" / "evidence_storage_policy.json",
        {
            "schema_version": "glyphser-evidence-storage-policy.v1",
            "mode": "versioned_audit",
            "required_paths": [
                "evidence/metadata/catalog.json",
                "evidence/traceability/index.json",
            ],
            "forbidden_globs": ["evidence/tmp/**"],
        },
    )
    (root / ".gitignore").write_text("evidence/tmp/**\n", encoding="utf-8")

    tracked = [
        "evidence/metadata/catalog.json",
        "evidence/traceability/index.json",
        "evidence/security/sbom.json",
    ]

    # point module constants to temp tree
    evidence_storage_policy_gate.POLICY = root / "governance" / "structure" / "evidence_storage_policy.json"
    evidence_storage_policy_gate.OUT = root / "evidence" / "gates" / "quality" / "evidence_storage_policy.json"

    report = evidence_storage_policy_gate.evaluate(root=root, tracked_paths=tracked)
    assert report["status"] == "PASS"
