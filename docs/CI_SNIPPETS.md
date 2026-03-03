# CI Integration Snippets

## GitHub Actions

```yaml
- name: Install Glyphser
  run: |
    python -m pip install --upgrade pip
    pip install -e .
- name: Determinism gate
  run: glyphser run --example hello --tree
```

## GitLab CI

```yaml
glyphser_verify:
  image: python:3.12
  script:
    - pip install -e .
    - glyphser run --example hello --format json
```

## Jenkins (Declarative Pipeline)

```groovy
stage('Glyphser Verify') {
  steps {
    sh 'python -m pip install --upgrade pip'
    sh 'pip install -e .'
    sh 'glyphser run --example hello --tree'
  }
}
```
