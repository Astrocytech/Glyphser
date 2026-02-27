#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.deploy.generate_bundle import main as generate_bundles  # noqa: E402
from tools.deploy.generate_env_manifest import main as generate_env  # noqa: E402
from tools.deploy.generate_migration_plan import main as generate_migration  # noqa: E402
from tools.deploy.validate_profile import main as validate_profile  # noqa: E402


def main() -> int:
    status = 0
    status |= generate_bundles()
    status |= generate_env()
    status |= generate_migration()
    status |= validate_profile()
    return status


if __name__ == "__main__":
    raise SystemExit(main())
