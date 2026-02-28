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
        [sys.executable, "tooling/materialize_doc_artifacts.py"],
        [sys.executable, "tooling/doc_code_separation_gate.py"],
        [sys.executable, "tooling/legacy_path_gate.py"],
        [sys.executable, "tooling/structural_invariants_gate.py"],
        [sys.executable, "tooling/schema_gate.py"],
        [sys.executable, "tooling/registry_gate.py"],
        [sys.executable, "tooling/api_contract_gate.py"],
        [sys.executable, "tooling/spec_lint.py"],
        [sys.executable, "tooling/conformance/cli.py", "run"],
        [sys.executable, "tooling/conformance/cli.py", "report"],
        [sys.executable, "tooling/vector_gate.py"],
        [sys.executable, "tooling/coverage_report.py"],
        [sys.executable, "tooling/fixtures_gate.py"],
        [sys.executable, "tooling/error_code_gate.py"],
        [sys.executable, "tooling/codegen/generate.py"],
        [sys.executable, "tooling/codegen/check_generated_drift.py"],
        [sys.executable, "tooling/codegen/clean_build_generate.py"],
        [sys.executable, "tooling/codegen/diff_fidelity.py"],
        [sys.executable, "-m", "pytest"],
        [sys.executable, "tooling/security_artifacts.py"],
        [sys.executable, "tooling/security_baseline_gate.py"],
        [sys.executable, "tooling/deploy/run_deployment_pipeline.py"],
        [sys.executable, "tooling/observability_gate.py"],
        [sys.executable, "tooling/external_validation_gate.py"],
        [sys.executable, "tooling/build_release_bundle.py"],
        [sys.executable, "tooling/release_evidence_gate.py"],
        [sys.executable, "tooling/reproducibility_check.py"],
        [sys.executable, "tooling/state_recovery_gate.py"],
        [sys.executable, "tooling/ga_release_gate.py"],
    ]


def main() -> int:
    for cmd in _steps():
        if _run(cmd) != 0:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
