#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

ROOT = Path(__file__).resolve().parents[2]
TEMPLATES = ROOT / "tools" / "codegen" / "templates"
OUT_DIR = ROOT / "generated"
SCHEMA_ROOTS = [ROOT / "schemas", ROOT / "schemas" / "pilot"]
REGISTRY_JSON = ROOT / "contracts" / "operator_registry.json"
CATALOG_MANIFEST = ROOT / "contracts" / "catalog-manifest.json"


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
    for record in records:
        operator_id = record.get("operator_id", "")
        func_name = _operator_stub_name(operator_id)
        blocks.append(f"def {func_name}(request: Dict[str, Any]) -> Dict[str, Any]:")
        blocks.append(f"    \"\"\"{operator_id} stub.\"\"\"")
        blocks.append(
            "    return {\"error\": emit_error(\"PRIMITIVE_UNSUPPORTED\", "
            "\"Generated stub not implemented\", operator_id=\"%s\")}" % operator_id
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
            "generated/models.py",
            "generated/operators.py",
            "generated/validators.py",
            "generated/error.py",
            "generated/bindings.py",
        ]
    ]

    manifest = {
        "generator": "tools/codegen/generate.py",
        "operator_registry_root_hash": _registry_root_hash(),
        "template_bundle_hash": _template_bundle_hash(),
        "schemas": _schema_manifest(),
        "outputs": [
            "generated/models.py",
            "generated/operators.py",
            "generated/validators.py",
            "generated/error.py",
            "generated/bindings.py",
        ],
        "outputs_with_hashes": output_hashes,
    }
    (OUT_DIR / "codegen_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    generate()
