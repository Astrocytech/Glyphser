#!/usr/bin/env python3
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

artifact_signing = importlib.import_module("runtime.glyphser.security.artifact_signing")
evidence_root = importlib.import_module("tooling.lib.path_config").evidence_root
write_json_report = importlib.import_module("tooling.security.report_io").write_json_report

TRUST_CONTRACT = ROOT / "governance" / "security" / "external_artifact_trust_contract.json"
STANDARDS_PROFILE = ROOT / "governance" / "security" / "security_standards_profile.json"


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload if isinstance(payload, dict) else {}


def _as_string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if isinstance(item, str) and str(item).strip()]


def main(argv: list[str] | None = None) -> int:
    _ = argv
    findings: list[str] = []

    trust = _load_json(TRUST_CONTRACT) if TRUST_CONTRACT.exists() else {}
    standards = _load_json(STANDARDS_PROFILE) if STANDARDS_PROFILE.exists() else {}
    if not trust:
        findings.append("missing_or_invalid_external_artifact_trust_contract")
    if not standards:
        findings.append("missing_or_invalid_security_standards_profile")

    upstream = sorted(_as_string_list(trust.get("accepted_repositories")))
    downstream = sorted(_as_string_list(standards.get("consumer_repos")))

    report = {
        "status": "PASS" if not findings else "FAIL",
        "findings": findings,
        "summary": {
            "upstream_integrations": len(upstream),
            "downstream_integrations": len(downstream),
            "federation_links": len(upstream) + len(downstream),
        },
        "metadata": {"gate": "security_federation_manifest"},
        "federation": {
            "upstream_integrations": upstream,
            "downstream_integrations": downstream,
        },
    }
    out = evidence_root() / "security" / "security_federation_manifest.json"
    write_json_report(out, report)
    sig = artifact_signing.sign_file(out, key=artifact_signing.current_key(strict=False))
    out.with_suffix(out.suffix + ".sig").write_text(sig + "\n", encoding="utf-8")
    print(f"SECURITY_FEDERATION_MANIFEST: {report['status']}")
    print(f"Report: {out}")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
