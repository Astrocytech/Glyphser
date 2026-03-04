#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _result_to_sarif(item: dict[str, Any]) -> dict[str, Any]:
    fname = str(item.get("filename", ""))
    line = int(item.get("line_number", 1) or 1)
    test_id = str(item.get("test_id", "bandit.unknown"))
    issue = str(item.get("issue_text", "Bandit finding"))
    severity = str(item.get("issue_severity", "LOW")).upper()
    confidence = str(item.get("issue_confidence", "LOW")).upper()
    return {
        "ruleId": test_id,
        "level": "error" if severity in {"HIGH", "MEDIUM"} else "warning",
        "message": {"text": issue},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": fname},
                    "region": {"startLine": line},
                }
            }
        ],
        "properties": {
            "severity": severity,
            "confidence": confidence,
            "cwe": item.get("issue_cwe", {}),
            "more_info": item.get("more_info"),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Convert Bandit JSON output to SARIF.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    output_path = Path(args.output)
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    results = payload.get("results", []) if isinstance(payload, dict) else []
    if not isinstance(results, list):
        results = []

    sarif = {
        "version": "2.1.0",
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "runs": [
            {
                "tool": {"driver": {"name": "bandit", "informationUri": "https://bandit.readthedocs.io/"}},
                "results": [_result_to_sarif(item) for item in results if isinstance(item, dict)],
            }
        ],
    }
    output_path.write_text(json.dumps(sarif, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
