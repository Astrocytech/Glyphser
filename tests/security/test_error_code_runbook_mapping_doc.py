from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_error_code_runbook_mapping_covers_required_failure_classes() -> None:
    doc = (ROOT / "governance" / "security" / "ERROR_CODE_RUNBOOK_MAPPING.md").read_text(encoding="utf-8")
    for cls in ("`prereq_failure`", "`infra_failure`", "`policy_failure`", "`control_failure`"):
        assert cls in doc
    for runbook in (
        "governance/security/GATE_RUNBOOK_INDEX.md",
        "governance/security/INCIDENT_RUNBOOKS.md",
        "governance/security/POLICY_GATE_LIFECYCLE.md",
        "governance/security/OPERATIONS.md",
    ):
        assert runbook in doc
