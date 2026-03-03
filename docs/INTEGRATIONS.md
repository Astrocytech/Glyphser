# Integrations

## GitHub Actions gate

Use `glyphser run --example hello` as a required PR check.

```yaml
- name: Install Glyphser
  run: pip install -e .
- name: Determinism smoke check
  run: glyphser run --example hello --tree
```

## GitLab CI gate

```yaml
glyphser_verify:
  image: python:3.12
  script:
    - pip install -e .
    - glyphser run --example hello --format json
```

## Jenkins gate

See `docs/CI_SNIPPETS.md`.

## Pipeline embedding API

Use `glyphser.verify(...)` to compute deterministic digests from model + input payloads.

## MLflow example

Use `examples/mlflow_integration.py` to log Glyphser digest + evidence path into an MLflow run.

## Ecosystem adapter direction

Planned adapter patterns:
- MLflow run post-check (record digest and evidence path as run metadata)
- Airflow/Prefect task wrapper around `glyphser run --example hello`
- Kubeflow step for evidence emission and artifact persistence
- Great Expectations post-validation hook for digest evidence attachment
