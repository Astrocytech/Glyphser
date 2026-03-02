# Contributing to Glyphser

Thank you for contributing to Glyphser.

This guide explains how to propose changes, run validation locally, and submit pull requests that are easy to review and merge.

## Before You Start
- Read `README.md` for project purpose and layout.
- Read `CODE_OF_CONDUCT.md` for expected behavior.
- For security issues, do not open a public issue. Follow `SECURITY.md`.

## Development Setup
1. Use Python `3.12+`.
2. Clone the repository and move to project root.
3. Create and activate a virtual environment.
4. Install dependencies:
   ```bash
   python -m pip install -e .
   ```

## Recommended First Checks
- Verify release flow:
  ```bash
  python tooling/release/verify_release.py
  ```
- Or run full pipeline directly:
  ```bash
  python tooling/commands/push_button.py
  ```

## Contribution Workflow
1. Create a branch from the current default branch.
2. Make focused, minimal changes for one concern at a time.
3. Add or update tests and documentation when behavior changes.
4. Run relevant local checks before opening a PR.
5. Open a pull request with clear context and evidence.

## What to Include in a Pull Request
- A short problem statement.
- What changed and why.
- How you validated the change (commands run, key outputs).
- Risk notes and rollback considerations, if applicable.
- Linked issue(s), if available.

## Quality Expectations
- Keep claims scoped to what is verifiable in this repository.
- Preserve deterministic behavior and reproducibility guarantees.
- Do not introduce undocumented breaking changes.
- Keep code and docs aligned with existing structure policies.

## Testing and Validation
Choose the smallest meaningful validation set for your change, then expand if needed.

Common commands:
```bash
python -m pytest
python tooling/conformance/cli.py run
python tooling/conformance/cli.py report
python tooling/validation/generate_project_inventory.py
```

If your change affects release or integrity workflows, also run:
```bash
python tooling/release/verify_release.py
```

## Commit Guidance
- Write clear commit messages in imperative mood.
- Keep commits scoped and reviewable.
- Avoid mixing unrelated refactors with functional changes.

Suggested format:
```text
<area>: <short summary>
```
Example:
```text
tooling: tighten release checksum validation error output
```

## Documentation Contributions
- Use plain English for user-facing docs.
- Keep technical claims precise and bounded.
- When adding new commands or files, update `README.md` and any relevant docs in `docs/`, `product/`, or `specs/`.

## Security Contributions
- Follow `SECURITY.md` for vulnerability disclosure.
- Do not publish exploit details before maintainers coordinate a fix and disclosure plan.

## Review and Merge
- Maintainers may request changes for correctness, scope, safety, or clarity.
- PRs are merged when checks pass and review concerns are resolved.

## Need Help
- Open a discussion or issue for design questions and non-sensitive bugs.
- For sensitive matters, use the private path in `SECURITY.md`.
