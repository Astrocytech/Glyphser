#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "governance" / "structure" / "spec_schema_map.json"
OUT = ROOT / "evidence" / "structure" / "spec_schema_map.json"


def _rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


def _tokens(name: str) -> List[str]:
    s = name.lower().replace(".schema.json", "").replace(".md", "")
    s = re.sub(r"^l[1-4][_-]", "", s)
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return [tok for tok in s.split("-") if tok]


def _display_name(tokens: List[str], acronyms: Dict[str, str]) -> str:
    parts = []
    for tok in tokens:
        if tok in acronyms:
            parts.append(acronyms[tok])
        elif tok == "nextbatch":
            parts.append("NextBatch")
        elif tok == "modelir":
            parts.append("ModelIR")
        else:
            parts.append(tok.capitalize())
    return "-".join(parts) + ".md"


def _score(a: List[str], b: List[str]) -> float:
    sa = set(a)
    sb = set(b)
    if not sa and not sb:
        return 1.0
    return len(sa & sb) / len(sa | sb)


def _resolve_schema_target(schema_path: Path, spec_dir: Path, acronyms: Dict[str, str]) -> Optional[Path]:
    preferred = spec_dir / _display_name(_tokens(schema_path.name), acronyms)
    if preferred.exists():
        return preferred

    md_files = sorted(spec_dir.glob("*.md"))
    if not md_files:
        return None

    stoks = _tokens(schema_path.name)
    best = None
    best_score = -1.0
    for md in md_files:
        score = _score(stoks, _tokens(md.name))
        if score > best_score:
            best = md
            best_score = score
    if best_score <= 0.0:
        return None
    return best


def evaluate() -> dict:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    layer_spec_dirs = cfg.get("layer_spec_dirs", {})
    manual_overrides = cfg.get("manual_overrides", {})
    acronyms = cfg.get("acronyms", {})

    schema_files = sorted((ROOT / "specs" / "schemas" / "layers").rglob("*.schema.json"))
    resolved = []
    missing_specs = []
    missing_layers = []

    for schema in schema_files:
        schema_rel = _rel(schema)
        if schema_rel in manual_overrides:
            target = ROOT / manual_overrides[schema_rel]
            if not target.exists():
                missing_specs.append({"schema": schema_rel, "expected_spec": _rel(target)})
                continue
            resolved.append({"schema": schema_rel, "spec": _rel(target), "source": "manual_override"})
            continue

        layer = schema.parent.name
        spec_dir_rel = layer_spec_dirs.get(layer)
        if not spec_dir_rel:
            missing_layers.append({"schema": schema_rel, "layer": layer})
            continue
        spec_dir = ROOT / spec_dir_rel
        target = _resolve_schema_target(schema, spec_dir, acronyms)
        if target is None or not target.exists():
            missing_specs.append({"schema": schema_rel, "expected_dir": spec_dir_rel})
            continue
        resolved.append({"schema": schema_rel, "spec": _rel(target), "source": "derived"})

    resolved_schema_set = {row["schema"] for row in resolved}
    unmapped_schemas = [_rel(p) for p in schema_files if _rel(p) not in resolved_schema_set]

    payload = {
        "status": "PASS" if not missing_specs and not missing_layers and not unmapped_schemas else "FAIL",
        "schema_count": len(schema_files),
        "mapped_count": len(resolved),
        "missing_spec_targets": missing_specs,
        "missing_layer_mapping": missing_layers,
        "unmapped_schemas": unmapped_schemas,
        "mappings": resolved,
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    return payload


def main() -> int:
    report = evaluate()
    if report["status"] == "PASS":
        print("SPEC_SCHEMA_MAP_GATE: PASS")
        return 0
    print("SPEC_SCHEMA_MAP_GATE: FAIL")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
