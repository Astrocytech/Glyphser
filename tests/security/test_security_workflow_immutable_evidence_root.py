from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = ROOT / ".github" / "workflows"


def test_security_workflows_enforce_run_scoped_evidence_root_and_guard() -> None:
    findings: list[str] = []
    for wf in sorted(WORKFLOWS.glob("*.yml")):
        text = wf.read_text(encoding="utf-8")
        if "tooling/security/" not in text:
            continue
        rel = str(wf.relative_to(ROOT)).replace("\\", "/")
        if "python tooling/security/evidence_run_dir_guard.py --run-id" not in text:
            findings.append(f"missing_evidence_guard:{rel}")
        if "GLYPHSER_EVIDENCE_ROOT: evidence/runs/${{ github.run_id }}/" not in text:
            findings.append(f"missing_run_scoped_evidence_root:{rel}")
    assert not findings, "security workflow evidence scope violations:\n" + "\n".join(findings)
