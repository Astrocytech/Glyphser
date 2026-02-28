#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "evidence" / "gates" / "structure" / "structural_invariants.json"


def _scan_text_files(base: Path, exts: set[str]) -> List[Path]:
    paths: List[Path] = []
    if not base.exists():
        return paths
    for path in base.rglob("*"):
        if path.is_file() and path.suffix.lower() in exts:
            paths.append(path)
    return sorted(paths)


def _check_no_json_vectors_in_tests() -> Dict[str, object]:
    violations = [str(p.relative_to(ROOT)).replace("\\", "/") for p in (ROOT / "tests").rglob("*.json")]
    return {
        "name": "no_json_vectors_in_tests",
        "status": "PASS" if not violations else "FAIL",
        "violations": violations,
    }


def _check_runtime_import_boundaries() -> Dict[str, object]:
    import_pat = re.compile(r"^\s*(from|import)\s+(governance|product|evidence)(\.|\b)")
    path_pat = re.compile(r"(governance/|product/|evidence/)")
    violations: List[Dict[str, object]] = []
    for path in _scan_text_files(ROOT / "runtime", {".py"}):
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
        for i, line in enumerate(lines, start=1):
            if import_pat.search(line) or path_pat.search(line):
                violations.append(
                    {
                        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
                        "line": i,
                        "text": line.strip()[:200],
                    }
                )
    return {
        "name": "runtime_boundary_no_governance_product_evidence",
        "status": "PASS" if not violations else "FAIL",
        "violations": violations,
    }


def _check_no_legacy_test_vector_paths() -> Dict[str, object]:
    violations: List[Dict[str, object]] = []
    targets = [ROOT / ".github", ROOT / "tooling", ROOT / "tests", ROOT / "governance", ROOT / "specs", ROOT / "docs", ROOT / "product"]
    allowlist = {
        "tooling/gates/structural_invariants_gate.py",
        "governance/structure/STRUCTURAL_INVARIANTS.md",
    }
    for base in targets:
        for path in _scan_text_files(base, {".py", ".md", ".txt", ".rst", ".yml", ".yaml", ".json", ".toml"}):
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            if rel in allowlist:
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for i, line in enumerate(lines, start=1):
                if "tests/conformance/vectors" in line:
                    violations.append(
                        {
                            "file": rel,
                            "line": i,
                            "text": line.strip()[:200],
                        }
                    )
    return {
        "name": "no_legacy_test_vector_paths",
        "status": "PASS" if not violations else "FAIL",
        "violations": violations,
    }


def _check_operator_vectors_source_of_truth() -> Dict[str, object]:
    violations: List[Dict[str, object]] = []
    targets = [ROOT / "tests", ROOT / "tooling", ROOT / ".github"]
    allowlist = {
        "tooling/gates/structural_invariants_gate.py",
        "governance/structure/STRUCTURAL_INVARIANTS.md",
        "specs/examples/operators/README.md",
    }
    for base in targets:
        for path in _scan_text_files(base, {".py", ".md", ".txt", ".rst", ".yml", ".yaml", ".json", ".toml"}):
            rel = str(path.relative_to(ROOT)).replace("\\", "/")
            if rel in allowlist:
                continue
            lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
            for i, line in enumerate(lines, start=1):
                if "specs/examples/operators" in line:
                    violations.append(
                        {
                            "file": rel,
                            "line": i,
                            "text": line.strip()[:200],
                        }
                    )
    canonical_dir = ROOT / "artifacts" / "inputs" / "vectors" / "primitives" / "operators"
    has_canonical_vectors = canonical_dir.exists() and any(canonical_dir.glob("*.json"))
    status = "PASS" if not violations and has_canonical_vectors else "FAIL"
    return {
        "name": "operator_vectors_source_of_truth",
        "status": status,
        "violations": violations,
        "canonical_dir": str(canonical_dir.relative_to(ROOT)).replace("\\", "/"),
        "has_canonical_vectors": has_canonical_vectors,
    }


def _check_generated_layout() -> Dict[str, object]:
    req_dirs = [
        ROOT / "artifacts" / "generated" / "build" / "codegen",
        ROOT / "artifacts" / "generated" / "build" / "codegen_staging",
        ROOT / "artifacts" / "generated" / "build" / "deploy",
        ROOT / "artifacts" / "generated" / "build" / "metadata",
        ROOT / "evidence/state",
    ]
    missing_dirs = [str(p.relative_to(ROOT)).replace("\\", "/") for p in req_dirs if not p.exists()]

    forbidden = [
        ROOT / "artifacts" / "generated" / "models.py",
        ROOT / "artifacts" / "generated" / "operators.py",
        ROOT / "artifacts" / "generated" / "validators.py",
        ROOT / "artifacts" / "generated" / "error.py",
        ROOT / "artifacts" / "generated" / "bindings.py",
        ROOT / "artifacts" / "generated" / "clean_build",
        ROOT / "artifacts" / "generated" / "codegen" / "clean_build",
        ROOT / "artifacts" / "generated" / "build_metadata",
        ROOT / "artifacts" / "generated" / "codegen",
        ROOT / "artifacts" / "generated" / "deploy",
        ROOT / "artifacts" / "generated" / "codegen_manifest.json",
        ROOT / "artifacts" / "generated" / "input_hashes.json",
        ROOT / "artifacts" / "generated" / "runtime",
        ROOT / "artifacts" / "generated" / "runtime_state",
    ]
    forbidden_present = [str(p.relative_to(ROOT)).replace("\\", "/") for p in forbidden if p.exists()]

    required_files = [
        ROOT / "runtime" / "glyphser" / "generated" / "models.py",
        ROOT / "runtime" / "glyphser" / "generated" / "operators.py",
        ROOT / "runtime" / "glyphser" / "generated" / "validators.py",
        ROOT / "runtime" / "glyphser" / "generated" / "error.py",
        ROOT / "runtime" / "glyphser" / "generated" / "bindings.py",
        ROOT / "artifacts" / "generated" / "build" / "metadata" / "codegen_manifest.json",
        ROOT / "artifacts" / "generated" / "build" / "metadata" / "input_hashes.json",
    ]
    missing_files = [str(p.relative_to(ROOT)).replace("\\", "/") for p in required_files if not p.exists()]

    status = "PASS" if not missing_dirs and not forbidden_present and not missing_files else "FAIL"
    return {
        "name": "generated_layout",
        "status": status,
        "missing_dirs": missing_dirs,
        "forbidden_present": forbidden_present,
        "missing_files": missing_files,
    }


def evaluate() -> Dict[str, object]:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    checks = [
        _check_no_json_vectors_in_tests(),
        _check_runtime_import_boundaries(),
        _check_no_legacy_test_vector_paths(),
        _check_operator_vectors_source_of_truth(),
        _check_generated_layout(),
    ]
    status = "PASS" if all(c["status"] == "PASS" for c in checks) else "FAIL"
    payload = {"status": status, "checks": checks}
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    payload = evaluate()
    if payload["status"] == "PASS":
        print("STRUCTURAL_INVARIANTS_GATE: PASS")
        return 0
    print("STRUCTURAL_INVARIANTS_GATE: FAIL")
    for c in payload["checks"]:
        if c["status"] == "FAIL":
            print(f" - {c['name']}: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
