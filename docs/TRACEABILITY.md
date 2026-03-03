# Evidence Traceability Index

Glyphser can generate a machine-readable index connecting fixture inputs, evidence outputs, and commit identity.

## Generate

```bash
python tooling/release/generate_traceability_index.py
```

or via:

```bash
make traceability
```

## Output

- `evidence/traceability/index.json`

Contains:
- `git_commit`
- fixture list with file inventory
- fixture digest hints
- key evidence files and SHA-256 digests

Use this file for internal audit trails and release verification traceability.
