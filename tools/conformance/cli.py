#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools import build_operator_registry  # noqa: E402
from tools import verify_doc_artifacts  # noqa: E402

RESULTS_DIR = ROOT / "conformance" / "results"
REPORTS_DIR = ROOT / "conformance" / "reports"
TEMPLATE = ROOT / "tools" / "conformance" / "report_template.json"


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _run_hello_core() -> bool:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "run_hello_core.py")],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stdout)
        print(proc.stderr)
    return proc.returncode == 0


def run() -> int:
    results = []

    verify_ok = (verify_doc_artifacts.main() == 0)
    results.append({"check": "verify_doc_artifacts", "status": "PASS" if verify_ok else "FAIL"})

    try:
        build_operator_registry.main()
        results.append({"check": "build_operator_registry", "status": "PASS"})
    except Exception as exc:  # pragma: no cover
        results.append({"check": "build_operator_registry", "status": f"FAIL: {exc}"})

    hello_ok = _run_hello_core()
    results.append({"check": "hello_core", "status": "PASS" if hello_ok else "FAIL"})

    payload = {"status": "PASS" if all(r["status"] == "PASS" for r in results) else "FAIL", "results": results}
    _write_json(RESULTS_DIR / "latest.json", payload)
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["status"] == "PASS" else 1


def verify() -> int:
    latest = RESULTS_DIR / "latest.json"
    if not latest.exists():
        print("missing conformance results: run first")
        return 1
    data = json.loads(latest.read_text(encoding="utf-8"))
    print(json.dumps(data, indent=2, sort_keys=True))
    return 0 if data.get("status") == "PASS" else 1


def report() -> int:
    latest = RESULTS_DIR / "latest.json"
    if not latest.exists():
        print("missing conformance results: run first")
        return 1
    results = json.loads(latest.read_text(encoding="utf-8"))
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    report = dict(template)
    report["status"] = results.get("status")
    report["results"] = results.get("results")
    _write_json(REPORTS_DIR / "latest.json", report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report.get("status") == "PASS" else 1


def main() -> int:
    parser = argparse.ArgumentParser(prog="glyphser-conformance")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("run", help="Run conformance suite")
    sub.add_parser("verify", help="Verify results")
    sub.add_parser("report", help="Generate report")

    args = parser.parse_args()
    if args.command == "run":
        return run()
    if args.command == "verify":
        return verify()
    if args.command == "report":
        return report()

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
