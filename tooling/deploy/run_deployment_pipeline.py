#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tooling.deploy.generate_bundle import main as generate_bundles  # noqa: E402
from tooling.deploy.generate_env_manifest import main as generate_env  # noqa: E402
from tooling.deploy.generate_migration_plan import main as generate_migration  # noqa: E402
from tooling.deploy.generate_overlays import main as generate_overlays  # noqa: E402
from tooling.deploy.validate_profile import main as validate_profile  # noqa: E402
from tooling.deploy.deploy_rollback_gate import main as deploy_rollback_gate  # noqa: E402


def main() -> int:
    status = 0
    status |= generate_bundles()
    status |= generate_overlays()
    status |= generate_env()
    status |= generate_migration()
    status |= validate_profile()
    status |= deploy_rollback_gate()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
