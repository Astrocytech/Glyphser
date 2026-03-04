#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
load_stage_s_policy = importlib.import_module("tooling.security.stage_s_policy").load_stage_s_policy
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report


def main(argv: list[str] | None = None) -> int:
    _ = argv
    cfg = load_stage_s_policy().get("artifact_classification", {})
    manifest_path = ROOT / str(cfg.get("manifest_path", "governance/security/artifact_classification_manifest.json"))
    required_retention = {x for x in cfg.get("required_retention_classes", []) if isinstance(x, str)}
    payload = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    artifacts = payload.get("artifacts", []) if isinstance(payload, dict) else []

    findings: list[str] = []
    seen_retention: set[str] = set()
    if not isinstance(artifacts, list):
        findings.append("invalid_artifact_manifest")
        artifacts = []

    for i, art in enumerate(artifacts):
        if not isinstance(art, dict):
            findings.append(f"invalid_artifact_entry:{i}")
            continue
        rel = str(art.get("path", ""))
        cls = str(art.get("classification", ""))
        retention = str(art.get("retention_class", ""))
        if not rel or not cls or not retention:
            findings.append(f"missing_fields:{i}")
            continue
        seen_retention.add(retention)
        if not (ROOT / rel).exists():
            findings.append(f"missing_artifact_file:{rel}")

    for retention in sorted(required_retention):
        if retention not in seen_retention:
            findings.append(f"missing_retention_class:{retention}")

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"entries": len(artifacts), "retention_classes": sorted(seen_retention)},
        "metadata": {"gate": "artifact_classification_gate"},
    }
    out = evidence_root() / "security" / "artifact_classification_gate.json"
    write_json_report(out, report)
    print(f"ARTIFACT_CLASSIFICATION_GATE: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
