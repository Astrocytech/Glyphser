from __future__ import annotations

import json
from pathlib import Path

from tooling.security import verify_branch_protection_live


def test_verify_branch_protection_live_dry_run(monkeypatch, tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    (repo / ".github").mkdir(parents=True)
    (repo / ".github" / "branch-protection.required.json").write_text(
        json.dumps({"required_status_checks": ["test-matrix"], "required_release_checks": []}) + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(verify_branch_protection_live, "ROOT", repo)
    monkeypatch.setattr(verify_branch_protection_live, "evidence_root", lambda: repo / "evidence")
    rc = verify_branch_protection_live.main(["--repo", "owner/repo", "--dry-run"])
    assert rc == 0
    payload = json.loads((repo / "evidence" / "security" / "branch_protection_live.json").read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
