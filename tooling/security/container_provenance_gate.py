#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tooling.lib.path_config import evidence_root


def main() -> int:
    policy = json.loads(
        (ROOT / "governance" / "security" / "container_provenance_policy.json").read_text(encoding="utf-8")
    )
    if not isinstance(policy, dict):
        raise ValueError("invalid container provenance policy")
    digest_manifest = ROOT / str(policy.get("container_digest_manifest", "")).strip()
    required_files = [ROOT / str(x) for x in policy.get("required_signature_files", []) if isinstance(x, str)]
    require_when_present = bool(policy.get("required_when_container_artifacts_present", True))
    publishing_enabled = bool(policy.get("container_publishing_enabled", False))
    env_enabled = os.environ.get("GLYPHSER_CONTAINER_PUBLISHING_ENABLED", "").strip().lower()
    if env_enabled in {"1", "true", "yes"}:
        publishing_enabled = True
    if env_enabled in {"0", "false", "no"}:
        publishing_enabled = False

    findings: list[str] = []
    skipped = False
    strict_mode = publishing_enabled
    has_container_artifacts = digest_manifest.exists()
    if require_when_present and not has_container_artifacts and not strict_mode:
        skipped = True
    else:
        if not digest_manifest.exists():
            findings.append(f"missing digest manifest: {digest_manifest.relative_to(ROOT)}")
        for path in required_files:
            if not path.exists():
                findings.append(f"missing provenance file: {path.relative_to(ROOT)}")

    status = "PASS" if not findings else "FAIL"
    payload: dict[str, Any] = {
        "status": status,
        "skipped": skipped,
        "strict_mode": strict_mode,
        "findings": findings,
    }
    out = evidence_root() / "security" / "container_provenance.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"CONTAINER_PROVENANCE_GATE: {status}")
    print(f"Report: {out}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
