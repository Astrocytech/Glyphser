#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "specs" / "contracts" / "openapi_public_api_v1.yaml"
STYLE_GUIDE = ROOT / "product" / "docs" / "API_STYLE_GUIDE.md"
LIFECYCLE = ROOT / "product" / "docs" / "API_LIFECYCLE_POLICY.md"


def load_contract(path: Path = CONTRACT) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_contract(doc: Dict[str, Any]) -> None:
    if str(doc.get("openapi", "")).strip() == "":
        raise ValueError("missing openapi version")
    info = doc.get("info", {})
    version = str(info.get("version", ""))
    if not version.startswith("1."):
        raise ValueError("public API major version must remain 1.x for Milestone 18")
    semver_policy = info.get("x-semver-policy", {})
    if semver_policy.get("major_breaking_requires_new_version") is not True:
        raise ValueError("missing semver major-breaking policy")
    if int(semver_policy.get("deprecation_window_releases", 0)) < 1:
        raise ValueError("invalid deprecation window")
    if int(semver_policy.get("minimum_support_window_months", 0)) < 12:
        raise ValueError("invalid minimum support window")
    paths = doc.get("paths", {})
    required = ["/v1/jobs", "/v1/jobs/{job_id}", "/v1/jobs/{job_id}/evidence", "/v1/jobs/{job_id}/replay"]
    for p in required:
        if p not in paths:
            raise ValueError(f"missing required endpoint: {p}")


def main() -> int:
    if not CONTRACT.exists():
        print(f"API_CONTRACT_GATE: FAIL missing {CONTRACT}")
        return 1
    if not STYLE_GUIDE.exists():
        print(f"API_CONTRACT_GATE: FAIL missing {STYLE_GUIDE}")
        return 1
    if not LIFECYCLE.exists():
        print(f"API_CONTRACT_GATE: FAIL missing {LIFECYCLE}")
        return 1
    try:
        validate_contract(load_contract(CONTRACT))
    except Exception as exc:
        print(f"API_CONTRACT_GATE: FAIL {exc}")
        return 1
    print("API_CONTRACT_GATE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

