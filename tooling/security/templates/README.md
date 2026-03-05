# Security Safe Default Templates

Use these templates when adding new security gates/workflows to keep required report fields and test structure consistent.

- `security_gate_template.py.tmpl`: Gate script skeleton with `status/findings/summary/metadata` output contract.
- `security_gate_test_template.py.tmpl`: Test skeleton with PASS/FAIL test hooks and report contract assertions.
- `security_workflow_template.yml.tmpl`: Workflow skeleton with pinned actions, deterministic env, preflight checks, and artifact upload wiring.
