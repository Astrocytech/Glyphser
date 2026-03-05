#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root
from tooling.security.report_io import write_json_report

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
LARGE_JSON_STREAM_THRESHOLD_BYTES = 1_000_000
TOP_LEVEL_KEY_RE = re.compile(r'^\s{2}"([^"]+)":')
SUPER_GATE_SCRIPT_RE = re.compile(r'"(tooling/security/[A-Za-z0-9._/-]+\.py)"')


def _stream_large_report(path: Path) -> dict[str, Any]:
    top_level_keys: list[str] = []
    seen_keys: set[str] = set()
    scripts: list[str] = []
    seen_scripts: set[str] = set()
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            key_match = TOP_LEVEL_KEY_RE.match(line)
            if key_match:
                key = key_match.group(1)
                if key not in seen_keys:
                    seen_keys.add(key)
                    top_level_keys.append(key)
            if path.name == "security_super_gate.json":
                for match in SUPER_GATE_SCRIPT_RE.finditer(line):
                    script = match.group(1)
                    if script not in seen_scripts:
                        seen_scripts.add(script)
                        scripts.append(script)
    return {"_streamed": True, "_top_level_keys": top_level_keys, "_super_gate_scripts": scripts}


def _load_json(path: Path) -> dict[str, Any] | None:
    if path.stat().st_size >= LARGE_JSON_STREAM_THRESHOLD_BYTES:
        return _stream_large_report(path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


def _canonical_sha256(payload: Any) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _security_run_id() -> str:
    for key in ("GLYPHSER_SECURITY_RUN_ID", "GITHUB_RUN_ID", "CI_PIPELINE_ID"):
        value = os.environ.get(key, "").strip()
        if value:
            return value
    return "local"


def main(argv: list[str] | None = None) -> int:
    _ = argv
    sec = evidence_root() / "security"
    findings: list[str] = []
    mappings: list[dict[str, Any]] = []
    reports = sorted(path for path in sec.glob("*.json") if path.name != "security_lineage_map.json")

    for report in reports:
        payload = _load_json(report)
        rel = str(report.relative_to(evidence_root())).replace("\\", "/")
        if payload is None:
            findings.append(f"invalid_report_json:{rel}")
            continue
        top_level_keys = sorted(payload.get("_top_level_keys", [])) if payload.get("_streamed") else sorted(payload.keys())
        for key in top_level_keys:
            mappings.append(
                {
                    "report": rel,
                    "field_path": key,
                    "source_artifacts": [rel],
                    "rule_id": "LINEAGE_SELF_FIELD",
                }
            )
        if report.name == "security_super_gate.json":
            if payload.get("_streamed"):
                for idx, script in enumerate(payload.get("_super_gate_scripts", [])):
                    if not str(script).endswith(".py"):
                        continue
                    source_report = f"evidence/security/{Path(str(script)).stem}.json"
                    mappings.append(
                        {
                            "report": rel,
                            "field_path": f"results[{idx}].status",
                            "source_artifacts": [source_report],
                            "rule_id": "LINEAGE_SUPER_GATE_COMPONENT_STATUS",
                        }
                    )
            else:
                rows = payload.get("results", [])
                if isinstance(rows, list):
                    for idx, row in enumerate(rows):
                        if not isinstance(row, dict):
                            continue
                        cmd = row.get("cmd", [])
                        script = str(cmd[1]) if isinstance(cmd, list) and len(cmd) >= 2 else ""
                        if not script.endswith(".py"):
                            continue
                        source_report = f"evidence/security/{Path(script).stem}.json"
                        mappings.append(
                            {
                                "report": rel,
                                "field_path": f"results[{idx}].status",
                                "source_artifacts": [source_report],
                                "rule_id": "LINEAGE_SUPER_GATE_COMPONENT_STATUS",
                            }
                        )

    mappings = sorted(
        mappings,
        key=lambda item: (str(item.get("report", "")), str(item.get("field_path", "")), str(item.get("rule_id", ""))),
    )
    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {"reports_scanned": len(reports), "lineage_mappings": len(mappings)},
        "metadata": {"gate": "security_lineage_map_artifact"},
        "mappings": mappings,
    }
    out = sec / "security_lineage_map.json"
    write_json_report(out, report)

    digest_payload = {
        "status": "PASS" if not findings else "FAIL",
        "findings": list(findings),
        "summary": {
            "run_id": _security_run_id(),
            "lineage_map_path": str(out.relative_to(evidence_root())).replace("\\", "/"),
            "lineage_mappings": len(mappings),
            "lineage_digest_sha256": _canonical_sha256(mappings),
        },
        "metadata": {"gate": "security_lineage_digest_artifact"},
    }
    digest_out = sec / "security_lineage_digest.json"
    write_json_report(digest_out, digest_payload)
    sig = artifact_signing.sign_file(digest_out, key=artifact_signing.current_key(strict=False))
    digest_out.with_suffix(digest_out.suffix + ".sig").write_text(sig + "\n", encoding="utf-8")

    print(f"SECURITY_LINEAGE_MAP_ARTIFACT: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
