# Security Scanning

CI security checks:

- `bandit -q -r glyphser runtime tooling`
- `pip-audit`

Run locally:

```bash
make security-scan
```

Policy:
- Security scan failures block CI on mainline workflow.
