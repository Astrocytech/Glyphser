# Integrations

## GitHub Actions gate

Use `glyphser verify hello-core` as a required PR check.

```yaml
- name: Install Glyphser
  run: pip install -e .
- name: Determinism smoke check
  run: glyphser verify hello-core --format text --tree
```

## GitLab CI gate

```yaml
glyphser_verify:
  image: python:3.12
  script:
    - pip install -e .
    - glyphser verify hello-core --format json
```

## Pipeline step

Use `glyphser snapshot` to emit an auditable manifest artifact from your pipeline run.
