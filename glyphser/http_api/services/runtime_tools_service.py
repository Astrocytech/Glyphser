from __future__ import annotations

from pathlib import Path
from typing import Any

from glyphser.http_api.controllers.runtime_tools_controller import RuntimeToolsController
from glyphser.http_api.util.naming import safe_filename


class RuntimeToolsService:
    def __init__(self, controller: RuntimeToolsController, *, repo_root: Path, work_root: Path) -> None:
        self._controller = controller
        self._repo_root = repo_root.resolve()
        self._work_root = work_root.resolve()

    def ir_validate(self, ir_dag: dict[str, Any]) -> dict[str, Any]:
        return self._controller.ir_validate(ir_dag)

    def trace_hash(self, records: list[dict[str, Any]]) -> str:
        return self._controller.trace_hash(records)

    def load_driver(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._controller.load_driver(request)

    def route_catalog(self) -> dict[str, Any]:
        return self._controller.route_catalog()

    def route_policy(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._controller.route_policy(request)

    def contract_validate(self, ir_dag: dict[str, Any], *, driver_request: dict[str, Any], mode: str) -> dict[str, Any]:
        return self._controller.contract_validate(ir_dag, driver_request=driver_request, mode=mode)

    def evidence_validate(self, request: dict[str, Any]) -> dict[str, Any]:
        return self._controller.evidence_validate(request)

    def next_batch(self, dataset: list[Any], cursor: int, batch_size: int) -> dict[str, Any]:
        return self._controller.next_batch(dataset, cursor, batch_size)

    def interface_hash(self, registry: dict[str, Any]) -> dict[str, Any]:
        return self._controller.interface_hash(registry)

    def api_interfaces(self, *, repo_root) -> list[dict[str, Any]]:
        return self._controller.api_interfaces(repo_root=repo_root)

    def write_trace_workspace(self, *, records: list[dict[str, Any]], out_path) -> dict[str, Any]:
        return self._controller.write_trace_workspace(records=records, out_path=out_path)

    def write_execution_certificate_workspace(self, *, evidence: dict[str, Any], out_path) -> dict[str, Any]:
        return self._controller.write_execution_certificate_workspace(evidence=evidence, out_path=out_path)

    def api_interfaces_from_repo(self) -> list[dict[str, Any]]:
        return self._controller.api_interfaces(repo_root=self._repo_root)

    def write_trace(self, *, records: list[dict[str, Any]], name: str) -> dict[str, Any]:
        filename = safe_filename(name, suffix=".json")
        out_path = (self._work_root / "traces" / filename).resolve()
        if self._work_root not in out_path.parents:
            raise PermissionError("trace path escapes workspace")
        return self._controller.write_trace_workspace(records=records, out_path=out_path)

    def write_execution_certificate(self, *, evidence: dict[str, Any], name: str) -> dict[str, Any]:
        filename = safe_filename(name, suffix=".json")
        out_path = (self._work_root / "certificates" / filename).resolve()
        if self._work_root not in out_path.parents:
            raise PermissionError("certificate path escapes workspace")
        return self._controller.write_execution_certificate_workspace(evidence=evidence, out_path=out_path)


def runtime_tools_service_factory(*, repo_root: Path, work_root: Path) -> RuntimeToolsService:
    return RuntimeToolsService(RuntimeToolsController(), repo_root=repo_root, work_root=work_root)
