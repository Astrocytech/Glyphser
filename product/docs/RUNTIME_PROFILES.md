# Runtime Profiles (Milestone 17)

Status: APPROVED FOR IMPLEMENTATION
Version: 0.1
Owner: Glyphser maintainers

## Purpose
Define runtime profile matrix with explicit constraints, supported features, deployment assumptions, reproducibility class, support tier, and test requirements.

## Profile Matrix

| Profile ID | Local Dev (`P1_LOCAL_DEV`) | Single-Node Prod (`P2_SINGLE_NODE_PROD`) | Multi-Node Regulated (`P3_MULTI_NODE_REGULATED`) |
| --- | --- | --- | --- |
| Primary intent | Fast deterministic developer loop | Production deterministic execution on one node | Compliance-sensitive distributed execution |
| Support tier | Tier 2 (best effort) | Tier 1 (primary) | Tier 0 (strict controls required) |
| Reproducibility class | R1 deterministic within host class | R1 deterministic across supported host class | R0/R1 based on declared policy and hardware class |
| Deployment assumptions | Linux host or WSL, Python 3.12+, local filesystem | Linux x86_64, pinned container/runtime, managed storage | Multi-node Linux cluster, controlled network zones, policy-enforced storage |
| CPU/GPU assumptions | CPU-only baseline; optional dev GPU | CPU required, GPU optional per workload | CPU/GPU mix allowed only if declared in profile manifest |
| Storage class | Local disk, non-HA | Durable single-node volume with backups | Durable replicated storage with encryption and retention controls |
| Network boundary | Local/private development network | Private service network with controlled ingress | Segmented network with policy enforcement and audit logging |
| Time sync requirement | NTP enabled, <= 500 ms drift | NTP enabled, <= 100 ms drift | NTP/PTP controls, <= 50 ms drift |
| Data classification ceiling | Internal/non-regulated | Internal + restricted operational data | Sensitive/regulated workloads |
| Residency constraint | Not guaranteed | Region-pinned if configured | Region/sovereignty enforced by policy |
| Tenancy model | Single-tenant | Single-tenant | Multi-tenant with strict namespace/RBAC isolation |
| Supported features | Verify/release flow, conformance, replay basics | Full release pipeline, evidence gate, reproducibility checks | Full controls + policy checks + compliance evidence chain |
| Unsupported examples | SLA-backed uptime, unbounded throughput, internet-facing multitenant control plane | Cross-region active-active, unmanaged dependency upgrades | Running without RBAC/audit, unmanaged keys, non-compliant storage |
| Non-functional baseline | Verify command <= 30 min on reference machine | Deterministic run success >= 99%, bounded queue latency | Deterministic and policy pass rates at compliance threshold |
| Max input/model envelope | Small/medium fixtures only | Declared production envelope per release | Declared regulated envelope only, policy-gated |
| Key management backend | Local key material for dev only | Managed KMS required for production secrets | KMS/HSM class required with custody controls |
| Observability baseline | Basic logs + verify output | Metrics/logs/traces + alerting | Full audit, lineage, and retention controls |
| Cost controls | Informational only | Budget alarms + quota enforcement | Budget/quota + policy enforcement and reporting |
| Commercial scope | Internal/self-hosted dev | Self-hosted customer production | Self-hosted regulated deployments |

## Test Requirements by Profile

| Profile ID | Required test/gate set |
| --- | --- |
| `P1_LOCAL_DEV` | `python tooling/verify_release.py`; core conformance suite; deterministic artifact checks |
| `P2_SINGLE_NODE_PROD` | `python tooling/push_button.py`; release evidence gate; reproducibility check; deployment smoke and rollback drill |
| `P3_MULTI_NODE_REGULATED` | All `P2` gates plus RBAC negative tests, audit integrity checks, recovery drills, compliance policy validation, external reproducibility confirmation |

## Profile Gate Criteria
- Every profile must declare:
- Constraints (resource, network, storage, compliance, residency).
- Supported feature set and explicit unsupported scenarios.
- Reproducibility class and support tier.
- Required test suite and release gate set.

Milestone 17 gate is met only when all profile rows are complete and approved.

## Rejection Criteria
- Missing constraints, unsupported examples, or test requirements.
- Ambiguous reproducibility guarantees.
- Profile claims production support without explicit support tier or required gates.
- Profile claims regulated support without residency, key management, and audit controls.

## Change Control
- Any profile change must include:
- Updated matrix row and version bump.
- Rationale in changelog/review note.
- Evidence that required profile tests still pass.

