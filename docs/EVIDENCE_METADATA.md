# Evidence Metadata Catalog

Glyphser maintains a canonical evidence metadata catalog for audit and CI checks.

## Schema

- `specs/schemas/evidence_metadata.schema.json`

## Generate

```bash
python tooling/release/generate_evidence_metadata.py
```

## Validate

```bash
python tooling/quality_gates/evidence_metadata_gate.py
```

## Output

- `evidence/metadata/catalog.json`
- Gate report: `evidence/gates/quality/evidence_metadata.json`

Each catalog entry includes:
- artifact id
- path
- SHA-256 digest
- evidence type
- source fixture/domain
- generating tool
- schema version
