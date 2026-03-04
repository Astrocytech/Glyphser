from __future__ import annotations

import json
from pathlib import Path

from tooling.security import apply_branch_protection


def test_apply_branch_protection_dry_run(monkeypatch, tmp_path: Path, capsys) -> None:
    repo = tmp_path / "repo"
    (repo / ".github").mkdir(parents=True)
    (repo / ".github" / "branch-protection.required.json").write_text(
        json.dumps({"required_status_checks": ["test-matrix", "security-matrix"], "required_release_checks": []})
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(apply_branch_protection, "ROOT", repo)
    rc = apply_branch_protection.main(["--repo", "owner/repo", "--dry-run"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "required_status_checks" in out
