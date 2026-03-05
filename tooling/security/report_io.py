from __future__ import annotations

import json
import os
import re
import tempfile
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # pragma: no cover - non-POSIX fallback
    fcntl = None

SCHEMA_VERSION = 1
_MONOTONIC_BASE = time.monotonic()
_WALL_CLOCK_BASE = datetime.now(UTC)
_ERROR_CODE_TOKEN_RE = re.compile(r"[^a-z0-9]+")
_INFRA_HINTS = (
    "timeout",
    "timed_out",
    "network",
    "dns",
    "connection",
    "unavailable",
    "temporary",
    "transient",
    "infra",
    "transport",
    "subprocess",
)
_PREREQ_HINTS = ("missing_env", "missing_tool", "missing_prereq", "missing_required", "unknown_selected_gate")
_POLICY_HINTS = ("policy", "signature", "schema", "review", "governance")
_CONTROL_FAMILY_KEYWORDS = {
    "identity": ("auth", "token", "role", "scope", "rbac"),
    "supply_chain": ("dependency", "sbom", "lockfile", "package", "container", "workflow"),
    "provenance": ("provenance", "signature", "attestation", "slsa", "integrity"),
    "evidence": ("evidence", "retention", "archive", "notarization"),
    "runtime_api": ("runtime_api", "replay", "quota", "abuse", "cooldown"),
    "telemetry": ("telemetry", "event", "observability", "trend"),
    "governance": ("policy", "governance", "review", "exception", "runbook"),
}
ROOT = Path(__file__).resolve().parents[2]
ESCALATION_MATRIX = ROOT / "governance" / "security" / "escalation_matrix.json"


def _default_escalation_matrix() -> dict[str, Any]:
    return {
        "severity_levels": {
            "critical": {"primary": "security-oncall", "fallback": "security-leadership", "max_ack_minutes": 15},
            "high": {"primary": "security-oncall", "fallback": "platform-oncall", "max_ack_minutes": 30},
            "medium": {"primary": "security-engineering", "fallback": "platform-oncall", "max_ack_minutes": 60},
        }
    }


def _load_escalation_matrix() -> dict[str, Any]:
    if not ESCALATION_MATRIX.exists():
        return _default_escalation_matrix()
    try:
        payload = json.loads(ESCALATION_MATRIX.read_text(encoding="utf-8"))
    except Exception:
        return _default_escalation_matrix()
    if not isinstance(payload, dict):
        return _default_escalation_matrix()
    return payload


def _sanitize_string(value: str) -> str:
    out: list[str] = []
    for ch in value:
        code = ord(ch)
        if ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif code < 32 or code == 127:
            out.append(f"\\u{code:04x}")
        else:
            out.append(ch)
    return "".join(out)


def _sanitize_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _sanitize_payload(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_sanitize_payload(item) for item in value]
    if isinstance(value, tuple):
        return [_sanitize_payload(item) for item in value]
    if isinstance(value, str):
        return _sanitize_string(value)
    return value


def _normalize_error_code(value: str) -> str:
    token = _ERROR_CODE_TOKEN_RE.sub("_", value.strip().lower()).strip("_")
    if not token:
        token = "unknown_error"
    return f"sec_{token}"


def _derive_error_codes(findings: Any) -> list[str]:
    if not isinstance(findings, list):
        return []
    out: list[str] = []
    seen: set[str] = set()
    for item in findings:
        if not isinstance(item, str):
            continue
        code = _normalize_error_code(item)
        if code in seen:
            continue
        seen.add(code)
        out.append(code)
    return out


def _split_failure_domains(findings: Any) -> dict[str, list[str]]:
    if not isinstance(findings, list):
        return {"transient_infra_failures": [], "security_control_failures": []}
    infra: list[str] = []
    control: list[str] = []
    seen_infra: set[str] = set()
    seen_control: set[str] = set()
    for item in findings:
        if not isinstance(item, str):
            continue
        text = item.strip().lower()
        if not text:
            continue
        code = _normalize_error_code(item)
        if any(hint in text for hint in _INFRA_HINTS):
            if code not in seen_infra:
                seen_infra.add(code)
                infra.append(code)
            continue
        if code not in seen_control:
            seen_control.add(code)
            control.append(code)
    return {"transient_infra_failures": infra, "security_control_failures": control}


def _classify_failure(text: str) -> str:
    lowered = text.strip().lower()
    if any(hint in lowered for hint in _PREREQ_HINTS):
        return "prereq_failure"
    if any(hint in lowered for hint in _POLICY_HINTS):
        return "policy_failure"
    if any(hint in lowered for hint in _INFRA_HINTS):
        return "infra_failure"
    return "control_failure"


def _top_level_failure_classification(findings: Any) -> dict[str, Any]:
    if not isinstance(findings, list):
        return {"failure_classification": "control_failure", "failure_classification_set": []}
    categories: list[str] = []
    seen: set[str] = set()
    for item in findings:
        if not isinstance(item, str):
            continue
        category = _classify_failure(item)
        if category in seen:
            continue
        seen.add(category)
        categories.append(category)
    if not categories:
        return {"failure_classification": "control_failure", "failure_classification_set": []}
    priority = {"control_failure": 3, "prereq_failure": 0, "infra_failure": 1, "policy_failure": 2}
    primary = sorted(categories, key=lambda c: priority.get(c, 99))[0]
    return {"failure_classification": primary, "failure_classification_set": categories}


def _derive_control_family_tags(gate: Any, findings: Any) -> list[str]:
    text_parts: list[str] = []
    if isinstance(gate, str):
        text_parts.append(gate)
    if isinstance(findings, list):
        text_parts.extend(item for item in findings if isinstance(item, str))
    corpus = " ".join(text_parts).lower()
    tags: list[str] = []
    for tag, keywords in _CONTROL_FAMILY_KEYWORDS.items():
        if any(keyword in corpus for keyword in keywords):
            tags.append(tag)
    if not tags:
        tags.append("governance")
    return tags


def _generated_at_utc() -> str:
    fixed = os.environ.get("GLYPHSER_FIXED_UTC", "").strip()
    if fixed:
        return fixed
    source_date_epoch = os.environ.get("SOURCE_DATE_EPOCH", "").strip()
    if source_date_epoch:
        try:
            return datetime.fromtimestamp(int(source_date_epoch), UTC).isoformat()
        except ValueError:
            pass
    return datetime.now(UTC).isoformat()


def clock_consistency_violation(now_utc: datetime, *, tolerance_seconds: float | None = None) -> str | None:
    """Detect wall-clock jumps by comparing elapsed wall time to monotonic elapsed time."""
    if os.environ.get("GLYPHSER_FIXED_UTC", "").strip() or os.environ.get("SOURCE_DATE_EPOCH", "").strip():
        return None
    if tolerance_seconds is None:
        raw = os.environ.get("GLYPHSER_CLOCK_CONSISTENCY_TOLERANCE_SECONDS", "5").strip() or "5"
        try:
            tolerance_seconds = float(raw)
        except ValueError:
            tolerance_seconds = 5.0
    monotonic_elapsed = max(0.0, time.monotonic() - _MONOTONIC_BASE)
    expected_wall = _WALL_CLOCK_BASE.timestamp() + monotonic_elapsed
    observed_wall = now_utc.timestamp()
    drift_seconds = observed_wall - expected_wall
    if abs(drift_seconds) <= tolerance_seconds:
        return None
    return (
        "clock_consistency_violation:"
        f"wall_vs_monotonic_drift_seconds:{drift_seconds:.3f}:"
        f"tolerance_seconds:{tolerance_seconds:.3f}"
    )


def _normalize_report_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = _sanitize_payload(dict(payload))
    if "status" in normalized:
        normalized.setdefault("schema_version", SCHEMA_VERSION)
        normalized.setdefault("findings", [])
        normalized.setdefault("summary", {})
        metadata = normalized.setdefault("metadata", {})
        if isinstance(metadata, dict):
            metadata.setdefault("generated_at_utc", _generated_at_utc())
            metadata.setdefault("tz", os.environ.get("TZ", ""))
            metadata.setdefault("lc_all", os.environ.get("LC_ALL", ""))
            metadata.setdefault("lang", os.environ.get("LANG", ""))
            metadata.setdefault("error_code_version", "v1")
            metadata.setdefault("error_codes", _derive_error_codes(normalized.get("findings", [])))
            metadata.setdefault("failure_domains", _split_failure_domains(normalized.get("findings", [])))
            failure_top = _top_level_failure_classification(normalized.get("findings", []))
            metadata.setdefault("failure_classification", failure_top["failure_classification"])
            metadata.setdefault("failure_classification_set", failure_top["failure_classification_set"])
            metadata.setdefault(
                "control_family_tags",
                _derive_control_family_tags(metadata.get("gate", ""), normalized.get("findings", [])),
            )
            if str(normalized.get("status", "")).upper() == "FAIL":
                metadata.setdefault("escalation_matrix", _load_escalation_matrix())
    return normalized


@contextmanager
def _advisory_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_handle:
        if fcntl is not None:
            fcntl.flock(lock_handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)


def write_json_report(path: Path, payload: dict[str, Any]) -> None:
    """Write a canonical report using atomic replace + fsync."""
    path.parent.mkdir(parents=True, exist_ok=True)
    body = json.dumps(_normalize_report_payload(payload), indent=2, sort_keys=True) + "\n"
    lock_path = path.parent / f".{path.name}.lock"

    with _advisory_lock(lock_path):
        fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
        tmp_path = Path(tmp_name)
        try:
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(body)
                handle.flush()
                os.fsync(handle.fileno())
            tmp_path.replace(path)
            dir_fd = os.open(path.parent, os.O_DIRECTORY)
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
        finally:
            if tmp_path.exists():
                tmp_path.unlink()
