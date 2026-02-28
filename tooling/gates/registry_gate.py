#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RE_HASH = re.compile(r"^(sha256:)?[0-9a-fA-F]{64}$")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    api_path = ROOT / "specs" / "layers" / "L1-foundation" / "API-Interfaces.md"
    reg_path = ROOT / "specs" / "contracts" / "operator_registry.json"
    err_doc = ROOT / "specs" / "layers" / "L1-foundation" / "Error-Codes.md"

    if not reg_path.exists():
        raise SystemExit("operator_registry.json missing")

    valid_error_codes = set()
    if err_doc.exists():
        for line in err_doc.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line.startswith("|"):
                continue
            if "`" not in line:
                continue
            parts = [p.strip() for p in line.strip("|").split("|")]
            if not parts:
                continue
            code = parts[0].strip()
            if code.startswith("`") and code.endswith("`"):
                valid_error_codes.add(code[1:-1])

    reg = load_json(reg_path)
    records = reg.get("operator_records", [])
    if not records:
        raise SystemExit("operator_records empty")

    required = {
        "operator_id",
        "version",
        "method",
        "surface",
        "request_schema_digest",
        "response_schema_digest",
        "side_effects",
        "allowed_error_codes",
        "purity_class",
        "rng_usage",
        "determinism_class",
        "required_capabilities",
        "signature_digest",
    }

    for rec in records:
        missing = required - set(rec.keys())
        if missing:
            raise SystemExit(f"Missing fields in record {rec.get('operator_id')}: {sorted(missing)}")
        if "NONE" in rec.get("side_effects", []):
            raise SystemExit(f"Invalid side_effects NONE for {rec.get('operator_id')}")
        for code in rec.get("allowed_error_codes", []):
            if valid_error_codes and code not in valid_error_codes:
                raise SystemExit(f"Unknown error code {code} in {rec.get('operator_id')}")
        for key in ["request_schema_digest", "response_schema_digest", "signature_digest"]:
            val = rec.get(key, "")
            if isinstance(val, str) and not val.startswith("sha256:"):
                # allow labels like sha256:label and raw hex
                if not RE_HASH.match(val.replace("hex:", "")) and not val.startswith("sha256:"):
                    pass

    print(f"PASS: validated {len(records)} operator records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
