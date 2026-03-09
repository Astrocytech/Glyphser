


```

           ██████         ███████████████                                                          
     ███████         ███████          ████  █████████████████                ████████████████      
  ████           ███████              ████  ██████  █████                       █████   █████      
  ███          ██████               ████    ██████  ████                         ████   █████      
  ███        ██████             █████       ██████  ████                          ███   █████      
   █████   ██████       █████████           ██████  ████                          ███   █████      
       ███████████████████       ██████     ██████  ████         ███████          ███   █████      
          ██████              ██████        ██████  ████       ███████████        ███   █████      
          █████            ████████   ███   ██████  ████       ███████████        ███   █████      
          ██████      ██████ ██████████     ██████  ████        ████████          ███   █████      
             ██████████    ████████         ██████  ████                          ███   █████      
                    ███████████             ██████  ████                         ████   █████      
             ██████     ██████              ██████  ██████                      █████   █████      
          ████        ██████                ██████████████████              █████████████████      
        ████       ███████                                                                         
         █████████████      
```



# Glyphser
Deterministic verification engine for machine learning execution.
 

**Glyphser Demo Edition**

This repository is the public Demo Edition of Glyphser. It is intended to
demonstrate selected architecture, workflows, and verification concepts of the
system in an openly shared form.

It is not a complete representation of the broader Glyphser system or of any
separate private, internal, proprietary, or unpublished components that are
not included in this repository.

Glyphser provides a reproducible execution framework that produces verifiable
artifacts for machine learning runs. Instead of relying on informal logs or
best-effort reproducibility, Glyphser records structured execution traces,
checkpoints, and certificates that allow independent verification of results.

The goal of the project is to make machine learning runs **deterministic,
inspectable, and verifiable**.

---

# Why Glyphser Exists

Machine learning systems often suffer from weak reproducibility:

- training runs cannot be reproduced exactly
- environment differences change results
- logs are incomplete or informal
- verification requires trust rather than evidence

Glyphser addresses this by introducing a deterministic execution model that
records cryptographically bound artifacts during execution.

These artifacts allow third parties to verify that a run was executed exactly
as declared.

---

# Core Ideas

Glyphser introduces several core concepts.

**Run Manifest**

A run begins with a manifest that defines:

- operators
- parameters
- inputs
- environment constraints

The manifest acts as the formal declaration of execution.

**Deterministic Execution**

Operators are executed through a deterministic runtime.  
Stable serialization and hashing ensure that identical runs produce identical
commitments.

**Execution Artifacts**

During execution, Glyphser generates structured artifacts such as:

- execution traces
- checkpoints
- execution certificates

These artifacts describe what occurred during the run.

**Independent Verification**

Verification tools can replay or inspect the artifacts to confirm that the run
matches its declaration.

---

# High-Level Architecture

Glyphser operates as a deterministic execution and verification layer.

Typical components include:

- Run manifest
- Operator registry
- Deterministic runtime
- Serialization and hashing layer
- Trace generation
- Checkpoint artifacts
- Execution certificate
- Verification tooling

The runtime executes declared operators and produces artifacts that encode the
history and state of the execution.

---

# Example Execution Flow

A simplified execution flow looks like this:

```text
Manifest
   │
   ▼
Operator Resolution
   │
   ▼
Deterministic Execution
   │
   ▼
Trace Generation
   │
   ▼
Checkpoint Creation
   │
   ▼
Execution Certificate
   │
   ▼
Verification
````

Each stage produces artifacts that contribute to the final verification result.

---

# Installation

Install Glyphser from source:

```bash
git clone https://github.com/Astrocytech/Glyphser.git
cd Glyphser
pip install -e .
```

Dependencies are defined in `pyproject.toml`.

---

# Quick Example

Example manifest:

```yaml
run:
  name: example_run

operators:
  - id: preprocess
    type: preprocessing_step

  - id: train
    type: training_step
```

Run execution:

```bash
glyphser run manifest.yaml
```

After execution, the runtime generates artifacts describing the run.

---

# Generated Artifacts

Typical artifact outputs include:

* **Trace artifacts**
  Ordered record of execution events.

* **Checkpoint artifacts**
  Serialized intermediate states of operators.

* **Execution certificate**
  Final verification object that binds the run identity and artifacts.

Artifacts can be inspected or verified using the verification tools.

---

# Verification

Glyphser supports independent verification of execution artifacts.

Verification typically checks:

* artifact integrity
* manifest consistency
* operator interface compatibility
* trace completeness

Verification tools can confirm that the artifacts correspond to the declared
execution.

---

# Use Cases

Glyphser can be used in environments where reproducibility and verification are
important.

Typical scenarios include:

* reproducible machine learning research
* regulated AI workflows
* audit-ready ML pipelines
* deterministic experiment tracking
* reproducibility validation for CI systems

---

# Documentation

Full technical documentation and the detailed architecture description are
available in the project documentation.

```text
docs/WHITEPAPER_public.md
```

The whitepaper describes the full design philosophy, artifact model, and
execution architecture.

---

# Project Status

Glyphser is an active research and engineering project focused on deterministic
verification of machine learning execution.

Interfaces and internal components may evolve as the system matures.

---

# License

Copyright (C) 2026 Damir Olejar / Astrocytech

Unless otherwise noted, the source code and original project files in this
repository are licensed under the GNU Affero General Public License, version 3
only (AGPL-3.0-only).

This repository is the public Demo Edition of Glyphser.

You may use, modify, and redistribute this repository under the terms of the
AGPL-3.0. If you modify it and distribute it, or make a modified version
available for users to interact with over a network, you must provide the
corresponding source code of that modified version under the same license.

Redistributions and modified versions must preserve the existing copyright
notices, license notices, and attribution notices identifying Astrocytech and
Glyphser, as applicable to the material included here.

Modified versions must be clearly marked as modified and must not be presented
as the original Glyphser Demo Edition. 

***Any use of existing or modified component MUST reference this original source of the project, including the name Glyphser and Astrocytech.***

This repository does not grant any rights to separate private, proprietary,
internal, or unpublished editions or components of Glyphser that are not
included here.

Third-party components, dependencies, or assets included in this repository,
if any, remain subject to their own respective licenses.

No trademark rights are granted by this license. “Astrocytech” and “Glyphser”
are names and marks reserved by their owner, where applicable.

Separate private, proprietary, internal, or unpublished components, if any, are
not included in this repository and are not licensed under this repository’s
AGPL-3.0 terms.

Access to any such separate non-public materials may be provided only under a
signed Non-Disclosure Agreement.

See `LICENSE` for the full license text.

---

# Contributing

Contributions, issue reports, and design discussions are welcome.

Please see `CONTRIBUTING.md` for contribution guidelines.



Below are several common citation styles for the repository.

---

### APA (7th edition)

```text
Astrocytech (2026). *Glyphser* (Version main) [Source code]. GitHub. [https://github.com/Astrocytech/Glyphser](https://github.com/Astrocytech/Glyphser)
```
---

### MLA (9th edition)
```text
Astrocytech *Glyphser*. GitHub, 2026, [https://github.com/Astrocytech/Glyphser](https://github.com/Astrocytech/Glyphser).
```
---

### Chicago (Author–Date)
```text
Astrocytech 2026. *Glyphser*. GitHub repository. [https://github.com/Astrocytech/Glyphser](https://github.com/Astrocytech/Glyphser).
```
---

### Chicago (Notes and Bibliography)
```text
Astrocytech *Glyphser*. GitHub repository. 2026. [https://github.com/Astrocytech/Glyphser](https://github.com/Astrocytech/Glyphser).
```
---

### IEEE
```text
Astrocytech, “Glyphser,” GitHub repository, 2026. [Online]. Available: [https://github.com/Astrocytech/Glyphser](https://github.com/Astrocytech/Glyphser)
```
---

### Harvard
```text
Astrocytech (2026) *Glyphser*. GitHub repository. Available at: [https://github.com/Astrocytech/Glyphser](https://github.com/Astrocytech/Glyphser).
```
---

### BibTeX (for LaTeX papers)

```bibtex
@software{glyphser2026,
  author = {Astrocytech},
  title = {Glyphser},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/Astrocytech/Glyphser}
}
```


