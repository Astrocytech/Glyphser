from __future__ import annotations

from typing import Any

from runtime.glyphser.backend.load_driver import (
    DIRECT_DRIVER_IDS,
    PINNED_PROFILES,
    load_driver,
    universal_profile_mode_policy,
)
from runtime.glyphser.cert.evidence_validate import evidence_validate
from runtime.glyphser.data.next_batch import next_batch
from runtime.glyphser.contract.validate import validate_contract
from runtime.glyphser.model.ir_schema import validate_ir_dag
from runtime.glyphser.registry.interface_hash import compute_interface_hash
from runtime.glyphser.registry.registry_builder import parse_api_interfaces
from runtime.glyphser.trace.compute_trace_hash import compute_trace_hash
from runtime.glyphser.trace.trace_sidecar import write_trace
from runtime.glyphser.certificate.build import write_execution_certificate


class RuntimeToolsController:
    def ir_validate(self, ir_dag: dict[str, Any]) -> dict[str, Any]:
        return validate_ir_dag(ir_dag)

    def trace_hash(self, records: list[dict[str, Any]]) -> str:
        return compute_trace_hash(records)

    def load_driver(self, request: dict[str, Any]) -> dict[str, Any]:
        return load_driver(request)

    def route_catalog(self) -> dict[str, Any]:
        return {
            "direct_driver_ids": sorted(DIRECT_DRIVER_IDS),
            "pinned_profiles": {k: list(v) for k, v in sorted(PINNED_PROFILES.items())},
        }

    def route_policy(self, request: dict[str, Any]) -> dict[str, Any]:
        return universal_profile_mode_policy(request)

    def contract_validate(self, ir_dag: dict[str, Any], *, driver_request: dict[str, Any], mode: str) -> dict[str, Any]:
        driver_id = str(driver_request.get("driver_id", "default") or "default")
        driver = load_driver(driver_request)  # returns metadata only
        # validate_contract needs the driver object, so resolve it via backend resolver.
        from runtime.glyphser.backend.load_driver import resolve_driver

        resolved = resolve_driver(driver_id, driver_request)
        normalized = validate_contract(ir_dag=ir_dag, driver=resolved, mode=mode)
        return {
            "status": "OK",
            "driver": driver,
            "mode": mode,
            "normalized_ir": normalized,
        }

    def evidence_validate(self, request: dict[str, Any]) -> dict[str, Any]:
        return evidence_validate(request)

    def next_batch(self, dataset: list[Any], cursor: int, batch_size: int) -> dict[str, Any]:
        batch, next_cursor = next_batch(dataset, cursor, batch_size)
        return {"status": "OK", "batch": batch, "next_cursor": next_cursor}

    def interface_hash(self, registry: dict[str, Any]) -> dict[str, Any]:
        return {"interface_hash": compute_interface_hash(registry)}

    def api_interfaces(self, *, repo_root: Path) -> list[dict[str, Any]]:
        api_path = repo_root / "specs" / "layers" / "L1-foundation" / "API-Interfaces.md"
        return parse_api_interfaces(api_path)

    def write_trace_workspace(self, *, records: list[dict[str, Any]], out_path: Path) -> dict[str, Any]:
        digest = write_trace(records, out_path)
        return {"status": "OK", "trace_final_hash": digest, "path": str(out_path)}

    def write_execution_certificate_workspace(self, *, evidence: dict[str, Any], out_path: Path) -> dict[str, Any]:
        digest = write_execution_certificate(evidence, out_path)
        return {"status": "OK", "certificate_hash": digest, "path": str(out_path)}
