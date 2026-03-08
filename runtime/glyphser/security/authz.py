"""Deterministic RBAC authorization checks."""

from __future__ import annotations

from typing import Iterable

ROLE_PERMISSIONS = {
    "admin": {
        "jobs:write",
        "jobs:read",
        "evidence:read",
        "replay:run",
        "security:admin",
    },
    "operator": {
        "jobs:write",
        "jobs:read",
        "evidence:read",
        "replay:run",
    },
    "auditor": {
        "jobs:read",
        "evidence:read",
    },
    "viewer": {
        "jobs:read",
    },
}


def authorize(action: str, roles: Iterable[str]) -> bool:
    if not isinstance(action, str) or not action:
        return False
    allowed = set()
    for role in roles:
        allowed.update(ROLE_PERMISSIONS.get(role, set()))
    return action in allowed
