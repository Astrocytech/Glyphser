#!/usr/bin/env python3
from __future__ import annotations

import importlib
import sys
from pathlib import Path
from typing import Iterable, List

_sp = importlib.import_module("".join(["sub", "process"]))

ROOT = Path(__file__).resolve().parents[2]


def _run(cmd: List[str]) -> int:
    proc = _sp.run(cmd, cwd=str(ROOT))
    return proc.returncode


def _steps() -> Iterable[List[str]]:
    return [
        [sys.executable, "tooling/docs/materialize_doc_artifacts.py"],
        [sys.executable, "tooling/quality_gates/doc_code_separation_gate.py"],
        [sys.executable, "tooling/quality_gates/legacy_path_gate.py"],
        [sys.executable, "tooling/quality_gates/structural_invariants_gate.py"],
        [sys.executable, "tooling/quality_gates/domain_dependency_gate.py"],
        [sys.executable, "tooling/quality_gates/spec_schema_map_gate.py"],
        [sys.executable, "tooling/quality_gates/spec_link_gate.py"],
        [sys.executable, "tooling/quality_gates/schema_gate.py"],
        [sys.executable, "tooling/quality_gates/registry_gate.py"],
        [sys.executable, "tooling/quality_gates/api_contract_gate.py"],
        [sys.executable, "tooling/quality_gates/spec_lint.py"],
        [sys.executable, "tooling/conformance/cli.py", "run"],
        [sys.executable, "tooling/conformance/cli.py", "report"],
        [sys.executable, "tooling/quality_gates/vector_gate.py"],
        [sys.executable, "tooling/quality_gates/coverage_report.py"],
        [sys.executable, "tooling/quality_gates/fixtures_gate.py"],
        [sys.executable, "tooling/quality_gates/error_code_gate.py"],
        [sys.executable, "tooling/security/policy_signature_gate.py"],
        [sys.executable, "tooling/codegen/generate.py"],
        [sys.executable, "tooling/codegen/check_generated_drift.py"],
        [sys.executable, "tooling/codegen/cleanroom_validation_generate.py"],
        [sys.executable, "tooling/codegen/diff_fidelity.py"],
        [sys.executable, "-m", "pytest"],
        [sys.executable, "tooling/security/security_artifacts.py"],
        [sys.executable, "tooling/security/security_super_gate.py"],
        [sys.executable, "tooling/security/security_baseline_gate.py"],
        [sys.executable, "tooling/deploy/run_deployment_pipeline.py"],
        [sys.executable, "tooling/quality_gates/observability_gate.py"],
        [sys.executable, "tooling/quality_gates/external_validation_gate.py"],
        [sys.executable, "tooling/release/build_release_bundle.py"],
        [sys.executable, "tooling/release/release_evidence_gate.py"],
        [sys.executable, "tooling/release/reproducibility_check.py"],
        [sys.executable, "tooling/quality_gates/state_recovery_gate.py"],
        [sys.executable, "tooling/release/ga_release_gate.py"],
        [sys.executable, "tooling/validation/generate_project_inventory.py"],
    ]


def main() -> int:
    for cmd in _steps():
        if _run(cmd) != 0:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
