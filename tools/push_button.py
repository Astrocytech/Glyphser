#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Iterable, List

ROOT = Path(__file__).resolve().parents[1]


def _run(cmd: List[str]) -> int:
    proc = subprocess.run(cmd, cwd=str(ROOT))
    return proc.returncode


def _steps() -> Iterable[List[str]]:
    return [
        [sys.executable, "tools/materialize_doc_artifacts.py"],
        [sys.executable, "tools/schema_gate.py"],
        [sys.executable, "tools/registry_gate.py"],
        [sys.executable, "tools/spec_lint.py"],
        [sys.executable, "tools/conformance/cli.py", "run"],
        [sys.executable, "tools/conformance/cli.py", "report"],
        [sys.executable, "tools/vector_gate.py"],
        [sys.executable, "tools/coverage_report.py"],
        [sys.executable, "tools/fixtures_gate.py"],
        [sys.executable, "tools/error_code_gate.py"],
        [sys.executable, "tools/codegen/generate.py"],
        [sys.executable, "tools/codegen/check_generated_drift.py"],
        [sys.executable, "tools/codegen/clean_build_generate.py"],
        [sys.executable, "tools/codegen/diff_fidelity.py"],
        [sys.executable, "-m", "pytest"],
        [sys.executable, "tools/deploy/run_deployment_pipeline.py"],
        [sys.executable, "tools/build_release_bundle.py"],
        [sys.executable, "tools/release_evidence_gate.py"],
        [sys.executable, "tools/reproducibility_check.py"],
    ]


def main() -> int:
    for cmd in _steps():
        if _run(cmd) != 0:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
