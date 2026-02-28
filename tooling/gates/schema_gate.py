import json
import pathlib
import hashlib

ROOT = pathlib.Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "specs" / "schemas"
META_SCHEMA_PATH = SCHEMA_DIR / "contract_schema_meta.json"


def canonical_json_bytes(obj):
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8")


def load_json(path):
    return json.loads(path.read_text())


def find_refs(obj):
    refs = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k == "$ref" and isinstance(v, str):
                refs.append(v)
            else:
                refs.extend(find_refs(v))
    elif isinstance(obj, list):
        for item in obj:
            refs.extend(find_refs(item))
    return refs


def validate_schema(schema):
    meta = load_json(META_SCHEMA_PATH)
    # Minimal meta validation: ensure required keys exist.
    for key in meta["required"]:
        if key not in schema:
            raise ValueError(f"Missing required key: {key}")
    xg = schema.get("x_glyphser", {})
    for key in meta["properties"]["x_glyphser"]["required"]:
        if key not in xg:
            raise ValueError(f"Missing x_glyphser.{key}")

    source_doc = xg.get("source_doc")
    if source_doc:
        source_path = ROOT / source_doc
        if not source_path.exists():
            raise ValueError(f"source_doc not found: {source_doc}")
        source_text = source_path.read_text()

    # Validate $ref targets exist (local refs only).
    for ref in find_refs(schema):
        if ref.startswith("#"):
            continue
        ref_path = (ROOT / ref).resolve() if not ref.startswith("specs/schemas/") else (ROOT / ref).resolve()
        if not ref_path.exists():
            raise ValueError(f"$ref target not found: {ref}")

    # Prose drift check: required top-level properties should appear in source doc.
    required = schema.get("required", [])
    props = schema.get("properties", {})
    for prop in required:
        if prop not in props:
            raise ValueError(f"Required property '{prop}' not defined in properties")
    prose_check = xg.get("prose_check", "strict")
    if source_doc and required and prose_check != "relaxed":
        for prop in required:
            if prop not in props:
                continue
            if prop not in source_text:
                raise ValueError(f"Required property '{prop}' not found in source doc: {source_doc}")


def main():
    if not SCHEMA_DIR.exists():
        raise SystemExit("specs/schemas/ directory missing")
    meta = load_json(META_SCHEMA_PATH)
    _ = meta  # placeholder to ensure meta is readable
    schema_paths = sorted(SCHEMA_DIR.rglob("*.schema.json"))
    if not schema_paths:
        raise SystemExit("No schema artifacts found")

    for path in schema_paths:
        schema = load_json(path)
        validate_schema(schema)
        _hash = hashlib.sha256(canonical_json_bytes(schema)).hexdigest()
        if not _hash:
            raise ValueError("Empty hash")

    print(f"PASS: validated {len(schema_paths)} schema artifacts")


if __name__ == "__main__":
    main()
