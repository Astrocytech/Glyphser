# Glyphser Public vs Private Repository Boundary Policy

Document Owner: Astrocytech  
Scope: Glyphser open-source repository  
Applies To: All contributors and maintainers

This document defines exactly what must remain **public** in the open-source
Glyphser repository and what must remain **private** in Astrocytech internal
repositories.

The goal is to prevent accidental exposure of proprietary material while
keeping the open-source project useful and trustworthy.

---------------------------------------------------------------------

# 1. Public Repository (Open Core)

The public repository contains only the **open-source Glyphser core** and the
minimal documentation needed for developers to use it.

## Core Source Code

glyphser/  
runtime/  
stubs/

These contain the deterministic verification engine and supporting runtime.

## Testing and Examples

tests/  
examples/

Allowed:
- unit tests
- determinism tests
- CLI tests
- small example pipelines
- demonstration workflows

Not allowed:
- customer pipelines
- enterprise workflows
- real production datasets
- proprietary model pipelines

## Developer Tooling

tooling/

Allowed:
- formatting scripts
- developer helpers
- CLI utilities
- development environment helpers

Not allowed:
- release pipelines
- signing infrastructure
- deployment tooling
- enterprise integrations
- customer-specific tools

## Documentation

docs/

Allowed documentation:

- Getting started
- Installation instructions
- Basic architecture overview
- Tutorials
- Examples
- Diagrams
- Docker quickstart
- Use cases

Not allowed in public docs:

- Evidence lifecycle governance
- Internal policies
- SLA definitions
- Certification processes
- Internal architecture roadmaps
- Security hardening procedures
- Release governance
- Boundary gate definitions

## Project Metadata

Allowed files:

README.md  
LICENSE  
CHANGELOG.md  
SECURITY.md  
CODE_OF_CONDUCT.md  
CONTRIBUTING.md  
VERSIONING.md  

## Developer Configuration

Allowed:

pyproject.toml  
requirements.lock  
Makefile  
Dockerfile  
mypy.ini  
.pre-commit-config.yaml  
.gitignore  

---------------------------------------------------------------------

# 2. Private Repository (Company/Internal)

The private repository contains **everything related to operating Glyphser as
a commercial product**.

Nothing in this section should appear in the public repository.

## Governance and Policy

Examples:

- governance models
- internal policies
- certification frameworks
- risk classification
- compliance frameworks
- evidence governance

Typical directories:

governance/  
policy/  
certification/

## Product Layer

Anything that turns Glyphser into a commercial product:

product/  
enterprise/  
business/

Examples:

- pricing models
- product packaging
- support model
- service offerings
- commercialization strategy
- internal roadmap

## Evidence Lifecycle and Audit Layer

Private materials:

- evidence lifecycle management
- evidence storage policy
- audit packaging
- investigation procedures
- traceability governance
- certification evidence packs

Typical directories:

evidence/  
audit/  
traceability/

## Release Infrastructure

Internal release infrastructure must remain private.

Examples:

distribution/  
release/  
signing/

Includes:

- signing keys
- release pipelines
- artifact publishing
- internal build systems

## Operational Runbooks

Never public:

- incident response
- deployment procedures
- operational playbooks
- infrastructure configuration
- internal SRE procedures

Typical directories:

ops/  
runbooks/  
infra/

## Customer Material

Never public:

- customer implementations
- client pipelines
- internal datasets
- integration configurations

## Internal Automation

Never public:

- internal prompts
- automation scripts
- repo management tools
- hardening scripts

Examples:

internal/  
prompts/  
automation/

---------------------------------------------------------------------

# 3. Generated or Local Files (Never Commit)

The following must be blocked by `.gitignore`:

coverage.xml  
*.trace.json  
*.evidence.json  
artifacts/  
evidence/  
notebooks/  
private/  
internal/

These are generated or local-only files and must not appear in the repository.

---------------------------------------------------------------------

# 4. Quick Checklist Before Every Commit

Before pushing to the public repo, verify:

1. No governance material is included
2. No enterprise modules are included
3. No operational runbooks are included
4. No customer pipelines or datasets are included
5. No release infrastructure is included
6. No internal automation scripts are included
7. No generated artifacts are included

If any of the above appear, they must be moved to the private repository.

---------------------------------------------------------------------

# 5. Principle

The public repository must contain only:

"The open-source verification engine and the minimal documentation needed
for developers to use it."

Everything related to **running a business around Glyphser** must remain
private.

---------------------------------------------------------------------

# 6. Decision Rule for Ambiguous Material

If a file or directory falls into one of the following categories, it must
remain private unless explicitly approved for publication:

1. Enables operating Glyphser as a commercial service
2. Describes internal governance or decision processes
3. Contains production operational procedures
4. Reveals commercial strategy or product packaging
5. Includes customer-specific data or integrations

If unsure, the default action is:

Move the material to the private repository.

---------------------------------------------------------------------

# 7. Expected Public Repository Structure

The public repository should roughly follow this structure:

glyphser/        core library  
runtime/         deterministic runtime  
stubs/           typing stubs  

tests/           unit tests  
examples/        example pipelines  

docs/            user documentation  

tooling/         developer helpers  

README.md  
LICENSE  
CHANGELOG.md  
SECURITY.md  
CONTRIBUTING.md  

pyproject.toml  
requirements.lock  
Dockerfile  
Makefile  

---------------------------------------------------------------------

# 8. Security and Key Material

The following must NEVER appear in the public repository:

- signing keys
- private certificates
- API keys
- infrastructure credentials
- production tokens
- internal URLs
- internal network architecture

If such material is accidentally committed:

1. Immediately revoke the credential
2. Remove the commit from history
3. Rotate all affected keys

---------------------------------------------------------------------

# 9. Release Pipeline Boundary

The public repository may include:

- basic CI for linting and tests
- build validation

The following must remain private:

- artifact publishing
- package signing
- deployment pipelines
- release orchestration
- infrastructure provisioning

---------------------------------------------------------------------

# 10. Policy Maintenance

This document must be reviewed whenever:

- new directories are introduced
- CI/CD infrastructure changes
- enterprise features are added
- the repository structure changes

Updates must be approved by the repository maintainer.

---------------------------------------------------------------------
