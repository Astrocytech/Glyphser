#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tooling.lib.path_config import generated_root

TEMPLATES = ROOT / "tooling" / "codegen" / "templates"
OUT_DIR = ROOT / "runtime" / "glyphser" / "_generated"
SCHEMA_ROOTS = [ROOT / "specs" / "schemas"]
REGISTRY_JSON = ROOT / "specs" / "contracts" / "operator_registry.json"
CATALOG_MANIFEST = ROOT / "specs" / "contracts" / "catalog-manifest.json"


@dataclass
class SchemaInfo:
    schema_id: str
    class_name: str
    properties: Dict[str, Dict[str, Any]]
    required: List[str]


def _sha256_hex_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_hex_path(path: Path) -> str:
    return _sha256_hex_bytes(path.read_bytes())


def _read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sanitize_identifier(value: str) -> str:
    value = re.sub(r"[^0-9a-zA-Z_]", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        return "Generated"
    if value[0].isdigit():
        value = f"_{value}"
    return value


def _class_name_from_schema(schema: Dict[str, Any], fallback: str) -> str:
    raw = schema.get("title") or schema.get("x_glyphser", {}).get("schema_id") or fallback
    parts = re.split(r"[\./:_-]+", raw)
    words = [p for p in parts if p]
    if not words:
        return "GeneratedModel"
    return "".join(w[:1].upper() + w[1:] for w in words)


def _collect_schemas() -> List[SchemaInfo]:
    schema_files: List[Path] = []
    for root in SCHEMA_ROOTS:
        if not root.exists():
            continue
        schema_files.extend(sorted(root.rglob("*.schema.json")))

    infos: List[SchemaInfo] = []
    for path in sorted(set(schema_files)):
        data = _read_json(path)
        schema_id = data.get("$id") or data.get("x_glyphser", {}).get("schema_id") or path.name
        class_name = _class_name_from_schema(data, path.stem)
        props = data.get("properties", {}) if isinstance(data.get("properties", {}), dict) else {}
        required = data.get("required", []) if isinstance(data.get("required", []), list) else []
        infos.append(SchemaInfo(schema_id=schema_id, class_name=class_name, properties=props, required=required))
    return infos


def _py_type(prop: Dict[str, Any]) -> str:
    ptype = prop.get("type")
    if isinstance(ptype, list):
        if "null" in ptype:
            non_null = [t for t in ptype if t != "null"]
            if len(non_null) == 1:
                return f"Optional[{_py_type({'type': non_null[0]})}]"
            return "Optional[Any]"
        return "Any"
    if ptype == "string":
        return "str"
    if ptype == "integer":
        return "int"
    if ptype == "number":
        return "float"
    if ptype == "boolean":
        return "bool"
    if ptype == "array":
        return "List[Any]"
    if ptype == "object":
        return "Dict[str, Any]"
    return "Any"


def _render_models(schemas: List[SchemaInfo]) -> str:
    blocks: List[str] = []
    for schema in schemas:
        blocks.append("@dataclass")
        blocks.append(f"class {schema.class_name}:")
        if not schema.properties:
            blocks.append("    pass")
            blocks.append("")
            continue
        for prop_name, prop in sorted(schema.properties.items()):
            field_name = _sanitize_identifier(prop_name)
            annotation = _py_type(prop)
            if prop_name not in schema.required:
                if not annotation.startswith("Optional["):
                    annotation = f"Optional[{annotation}]"
                blocks.append(f"    {field_name}: {annotation} = None")
            else:
                blocks.append(f"    {field_name}: {annotation}")
        blocks.append("")
    return "\n".join(blocks).strip() + "\n"


def _operator_stub_name(operator_id: str) -> str:
    return _sanitize_identifier(operator_id.replace(".", "_"))


def _render_operator_stubs(records: Iterable[Dict[str, Any]]) -> str:
    blocks: List[str] = []
    implemented = {
        "Glyphser.Backend.LoadDriver",
        "Glyphser.IO.SaveCheckpoint",
        "Glyphser.Checkpoint.Restore",
        "Glyphser.Checkpoint.CheckpointMigrate",
        "Glyphser.Config.ManifestMigrate",
        "Glyphser.Import.LegacyFramework",
        "Glyphser.DifferentialPrivacy.Apply",
        "Glyphser.Model.Forward",
        "Glyphser.Model.ModelIR_Executor",
        "Glyphser.TMMU.PrepareMemory",
        "Glyphser.Certificate.EvidenceValidate",
        "Glyphser.Trace.TraceMigrate",
        "Glyphser.Registry.VersionCreate",
        "Glyphser.Registry.StageTransition",
        "Glyphser.Tracking.RunCreate",
        "Glyphser.Tracking.RunStart",
        "Glyphser.Tracking.RunEnd",
        "Glyphser.Tracking.MetricLog",
        "Glyphser.Tracking.ArtifactPut",
        "Glyphser.Tracking.ArtifactGet",
        "Glyphser.Tracking.ArtifactList",
        "Glyphser.Tracking.ArtifactTombstone",
        "Glyphser.Monitor.Register",
        "Glyphser.Monitor.Emit",
        "Glyphser.Monitor.DriftCompute",
    }
    for record in records:
        operator_id = record.get("operator_id", "")
        func_name = _operator_stub_name(operator_id)
        blocks.append(f"def {func_name}(request: Dict[str, Any]) -> Dict[str, Any]:")
        blocks.append(f"    \"\"\"{operator_id} stub.\"\"\"")
        if operator_id in implemented:
            blocks.append("    if not isinstance(request, dict):")
            blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            blocks.append("    if request.get(\"force_error\") is True:")
            blocks.append("        code = request.get(\"error_code\") or \"CONTRACT_VIOLATION\"")
            blocks.append("        ctx = {")
            blocks.append("            \"operator_id\": \"%s\"," % operator_id)
            blocks.append("            \"t\": \"placeholder\",")
            blocks.append("            \"node_id\": \"placeholder\",")
            blocks.append("            \"instr\": \"placeholder\",")
            blocks.append("            \"backend_binary_hash\": \"placeholder\",")
            blocks.append("            \"failure_operator\": \"placeholder\",")
            blocks.append("            \"driver_runtime_fingerprint_hash\": \"placeholder\",")
            blocks.append("            \"replay_token\": \"placeholder\",")
            blocks.append("            \"dataset_key\": \"placeholder\",")
            blocks.append("            \"global_position\": \"placeholder\",")
            blocks.append("            \"cardinality\": \"placeholder\",")
            blocks.append("            \"shape_in\": \"placeholder\",")
            blocks.append("            \"shape_expected\": \"placeholder\",")
            blocks.append("            \"size\": \"placeholder\",")
            blocks.append("            \"capacity\": \"placeholder\",")
            blocks.append("            \"arena\": \"placeholder\",")
            blocks.append("            \"logical_slot\": \"placeholder\",")
            blocks.append("            \"offset\": \"placeholder\",")
            blocks.append("            \"peak_required_bytes\": \"placeholder\",")
            blocks.append("            \"state_hash\": \"placeholder\",")
            blocks.append("            \"registered_hash\": \"placeholder\",")
            blocks.append("            \"stage_id\": \"placeholder\",")
            blocks.append("            \"ir_hash\": \"placeholder\",")
            blocks.append("            \"grad_hash\": \"placeholder\",")
            blocks.append("            \"rng_offset_before\": \"placeholder\",")
            blocks.append("            \"rng_offset_after\": \"placeholder\",")
            blocks.append("            \"required\": \"placeholder\",")
            blocks.append("            \"accountant\": \"placeholder\",")
            blocks.append("            \"accountant_type\": \"placeholder\",")
            blocks.append("            \"sigma_map_hash\": \"placeholder\",")
            blocks.append("            \"clipping_strategy\": \"placeholder\",")
            blocks.append("            \"cumulative_epsilon\": \"placeholder\",")
            blocks.append("            \"target_epsilon\": \"placeholder\",")
            blocks.append("        }")
            blocks.append("        return {\"error\": emit_error(code, \"invalid request\", **ctx)}")
            if operator_id == "Glyphser.IO.SaveCheckpoint":
                blocks.append("    try:")
                blocks.append("        state = request.get(\"state\", {})")
                blocks.append("        path = request.get(\"path\")")
                blocks.append("        if not path:")
                blocks.append("            return {\"error\": emit_error(\"INPUT_MISSING\", \"missing path\", operator_id=\"%s\")}" % operator_id)
                blocks.append("        digest = save_checkpoint(state, Path(path))")
                blocks.append("        return {\"checkpoint_hash\": digest}")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Checkpoint.Restore":
                blocks.append("    try:")
                blocks.append("        result = restore_checkpoint(request)")
                blocks.append("        return result")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Checkpoint.CheckpointMigrate":
                blocks.append("    try:")
                blocks.append("        return checkpoint_migrate(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Config.ManifestMigrate":
                blocks.append("    try:")
                blocks.append("        return manifest_migrate(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Import.LegacyFramework":
                blocks.append("    try:")
                blocks.append("        return legacy_framework_import(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.DifferentialPrivacy.Apply":
                blocks.append("    try:")
                blocks.append("        return dp_apply(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Model.Forward":
                blocks.append("    try:")
                blocks.append("        return forward(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Model.ModelIR_Executor":
                blocks.append("    try:")
                blocks.append("        return model_ir_execute(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.TMMU.PrepareMemory":
                blocks.append("    try:")
                blocks.append("        return prepare_memory(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Certificate.EvidenceValidate":
                blocks.append("    try:")
                blocks.append("        return evidence_validate(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Trace.TraceMigrate":
                blocks.append("    try:")
                blocks.append("        return migrate_trace(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Registry.VersionCreate":
                blocks.append("    try:")
                blocks.append("        return version_create(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Registry.StageTransition":
                blocks.append("    try:")
                blocks.append("        return stage_transition(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Tracking.RunCreate":
                blocks.append("    try:")
                blocks.append("        return run_create(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Tracking.RunStart":
                blocks.append("    try:")
                blocks.append("        return run_start(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Tracking.RunEnd":
                blocks.append("    try:")
                blocks.append("        return run_end(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Tracking.MetricLog":
                blocks.append("    try:")
                blocks.append("        return metric_log(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Tracking.ArtifactPut":
                blocks.append("    try:")
                blocks.append("        return artifact_put(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Tracking.ArtifactGet":
                blocks.append("    try:")
                blocks.append("        return artifact_get(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Tracking.ArtifactList":
                blocks.append("    try:")
                blocks.append("        return artifact_list(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Tracking.ArtifactTombstone":
                blocks.append("    try:")
                blocks.append("        return artifact_tombstone(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Monitor.Register":
                blocks.append("    try:")
                blocks.append("        return monitor_register(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Monitor.Emit":
                blocks.append("    try:")
                blocks.append("        return monitor_emit(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Monitor.DriftCompute":
                blocks.append("    try:")
                blocks.append("        return drift_compute(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
            elif operator_id == "Glyphser.Backend.LoadDriver":
                blocks.append("    try:")
                blocks.append("        return load_driver(request)")
                blocks.append("    except Exception:")
                blocks.append("        return {\"error\": emit_error(\"CONTRACT_VIOLATION\", \"invalid request\", operator_id=\"%s\")}" % operator_id)
        else:
            blocks.append("    if isinstance(request, dict) and request.get(\"force_error\") is True:")
            blocks.append("        code = request.get(\"error_code\") or \"PRIMITIVE_UNSUPPORTED\"")
            blocks.append("        ctx = {")
            blocks.append("            \"operator_id\": \"%s\"," % operator_id)
            blocks.append("            \"t\": \"placeholder\",")
            blocks.append("            \"node_id\": \"placeholder\",")
            blocks.append("            \"instr\": \"placeholder\",")
            blocks.append("            \"backend_binary_hash\": \"placeholder\",")
            blocks.append("            \"failure_operator\": \"placeholder\",")
            blocks.append("            \"driver_runtime_fingerprint_hash\": \"placeholder\",")
            blocks.append("            \"replay_token\": \"placeholder\",")
            blocks.append("            \"dataset_key\": \"placeholder\",")
            blocks.append("            \"global_position\": \"placeholder\",")
            blocks.append("            \"cardinality\": \"placeholder\",")
            blocks.append("            \"shape_in\": \"placeholder\",")
            blocks.append("            \"shape_expected\": \"placeholder\",")
            blocks.append("            \"size\": \"placeholder\",")
            blocks.append("            \"capacity\": \"placeholder\",")
            blocks.append("            \"arena\": \"placeholder\",")
            blocks.append("            \"logical_slot\": \"placeholder\",")
            blocks.append("            \"offset\": \"placeholder\",")
            blocks.append("            \"peak_required_bytes\": \"placeholder\",")
            blocks.append("            \"state_hash\": \"placeholder\",")
            blocks.append("            \"registered_hash\": \"placeholder\",")
            blocks.append("            \"stage_id\": \"placeholder\",")
            blocks.append("            \"ir_hash\": \"placeholder\",")
            blocks.append("            \"grad_hash\": \"placeholder\",")
            blocks.append("            \"rng_offset_before\": \"placeholder\",")
            blocks.append("            \"rng_offset_after\": \"placeholder\",")
            blocks.append("            \"required\": \"placeholder\",")
            blocks.append("            \"accountant\": \"placeholder\",")
            blocks.append("            \"accountant_type\": \"placeholder\",")
            blocks.append("            \"sigma_map_hash\": \"placeholder\",")
            blocks.append("            \"clipping_strategy\": \"placeholder\",")
            blocks.append("            \"cumulative_epsilon\": \"placeholder\",")
            blocks.append("            \"target_epsilon\": \"placeholder\",")
            blocks.append("        }")
            blocks.append("        return {\"error\": emit_error(code, \"invalid request\", **ctx)}")
            blocks.append(
                "    return {\"error\": emit_error(\"PRIMITIVE_UNSUPPORTED\", "
                "\"Generated stub not implemented\", operator_id=\"%s\", "
                "t=\"placeholder\", node_id=\"placeholder\", instr=\"placeholder\", backend_binary_hash=\"placeholder\")}"
                % operator_id
            )
        blocks.append("")
    return "\n".join(blocks).strip() + "\n"


def _render_validators(schemas: List[SchemaInfo]) -> str:
    blocks: List[str] = []
    for schema in schemas:
        fn = f"validate_{_sanitize_identifier(schema.class_name)}"
        blocks.append(f"def {fn}(obj: Any) -> List[str]:")
        blocks.append("    errors: List[str] = []")
        blocks.append("    if not isinstance(obj, dict):")
        blocks.append("        return [\"expected object\"]")
        for req in schema.required:
            field = _sanitize_identifier(req)
            blocks.append(f"    if '{req}' not in obj:")
            blocks.append(f"        errors.append(\"missing {field}\")")
        for prop_name, prop in sorted(schema.properties.items()):
            field = _sanitize_identifier(prop_name)
            ptype = prop.get("type")
            if not ptype:
                continue
            blocks.append(f"    if '{prop_name}' in obj:")
            if ptype == "string":
                blocks.append(f"        if not isinstance(obj['{prop_name}'], str):")
                blocks.append(f"            errors.append(\"{field} must be string\")")
            elif ptype == "integer":
                blocks.append(f"        if not isinstance(obj['{prop_name}'], int):")
                blocks.append(f"            errors.append(\"{field} must be integer\")")
            elif ptype == "number":
                blocks.append(f"        if not isinstance(obj['{prop_name}'], (int, float)):")
                blocks.append(f"            errors.append(\"{field} must be number\")")
            elif ptype == "boolean":
                blocks.append(f"        if not isinstance(obj['{prop_name}'], bool):")
                blocks.append(f"            errors.append(\"{field} must be boolean\")")
            elif ptype == "array":
                blocks.append(f"        if not isinstance(obj['{prop_name}'], list):")
                blocks.append(f"            errors.append(\"{field} must be array\")")
            elif ptype == "object":
                blocks.append(f"        if not isinstance(obj['{prop_name}'], dict):")
                blocks.append(f"            errors.append(\"{field} must be object\")")
        blocks.append("    return errors")
        blocks.append("")
    return "\n".join(blocks).strip() + "\n"


def _load_template(name: str) -> str:
    path = TEMPLATES / name
    return path.read_text(encoding="utf-8")


def _template_bundle_hash() -> str:
    entries = []
    for path in sorted(TEMPLATES.glob("*.tpl")):
        entries.append({"name": path.name, "sha256": _sha256_hex_path(path)})
    return _sha256_hex_bytes(json.dumps(entries, sort_keys=True).encode("utf-8"))


def _schema_manifest() -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    for root in SCHEMA_ROOTS:
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.schema.json")):
            entries.append(
                {
                    "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                    "sha256": _sha256_hex_path(path),
                }
            )
    return entries


def _registry_root_hash() -> str:
    if CATALOG_MANIFEST.exists():
        data = _read_json(CATALOG_MANIFEST)
        return data.get("derived_identities", {}).get("operator_registry_root_hash", "")
    if REGISTRY_JSON.exists():
        return _sha256_hex_path(REGISTRY_JSON)
    return ""


def generate() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (generated_root() / "metadata").mkdir(parents=True, exist_ok=True)
    (generated_root() / "codegen").mkdir(parents=True, exist_ok=True)

    schema_infos = _collect_schemas()
    registry = _read_json(REGISTRY_JSON)
    records = registry.get("operator_records", [])

    source_summary = "registry+schemas"

    models_out = _load_template("models.py.tpl").format(
        source_summary=source_summary,
        class_blocks=_render_models(schema_infos),
    )
    (OUT_DIR / "models.py").write_text(models_out, encoding="utf-8")

    operators_out = _load_template("operators.py.tpl").format(
        source_summary=source_summary,
        stub_blocks=_render_operator_stubs(records),
    )
    (OUT_DIR / "operators.py").write_text(operators_out, encoding="utf-8")

    validators_out = _load_template("validators.py.tpl").format(
        source_summary=source_summary,
        validator_blocks=_render_validators(schema_infos),
    )
    (OUT_DIR / "validators.py").write_text(validators_out, encoding="utf-8")

    error_out = _load_template("error.py.tpl").format(source_summary=source_summary)
    (OUT_DIR / "error.py").write_text(error_out, encoding="utf-8")

    bindings_out = _load_template("bindings.py.tpl").format(source_summary=source_summary)
    (OUT_DIR / "bindings.py").write_text(bindings_out, encoding="utf-8")

    output_hashes = [
        {"path": path, "sha256": _sha256_hex_path(ROOT / path)}
        for path in [
            "runtime/glyphser/_generated/models.py",
            "runtime/glyphser/_generated/operators.py",
            "runtime/glyphser/_generated/validators.py",
            "runtime/glyphser/_generated/error.py",
            "runtime/glyphser/_generated/bindings.py",
        ]
    ]

    manifest = {
        "generator": "tooling/codegen/generate.py",
        "operator_registry_root_hash": _registry_root_hash(),
        "template_bundle_hash": _template_bundle_hash(),
        "schemas": _schema_manifest(),
        "outputs": [
            "runtime/glyphser/_generated/models.py",
            "runtime/glyphser/_generated/operators.py",
            "runtime/glyphser/_generated/validators.py",
            "runtime/glyphser/_generated/error.py",
            "runtime/glyphser/_generated/bindings.py",
        ],
        "outputs_with_hashes": output_hashes,
    }
    (generated_root() / "metadata" / "codegen_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    codegen_index = {
        "canonical_runtime_generated_root": "runtime/glyphser/_generated",
        "runtime_generated_outputs": output_hashes,
    }
    (generated_root() / "codegen" / "index.json").write_text(
        json.dumps(codegen_index, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    # write input hash manifest for drift checks
    import sys as _sys  # noqa: E402
    _sys.path.insert(0, str(ROOT))
    from tooling.codegen.input_hash_manifest import main as _input_manifest  # noqa: E402
    _input_manifest()


if __name__ == "__main__":
    generate()
