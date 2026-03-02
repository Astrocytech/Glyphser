# Release Policy Delta (Milestone 30)

## Enforced Claim Rules
- Unscoped use of `universal` is blocked by CI claim gate.
- Every compatibility and certification statement must include a scope label.

## Support Tier Mapping
- Tier 1 (`tier_1_certified`): milestone status PASS with gate status PASS.
- Tier 2 (`tier_2_compatible_by_contract`): milestone status BLOCKED/partial but gate status PASS by explicit policy.
- Tier 3 (`tier_3_unvalidated`): gate status not PASS or missing evidence.

## Active Scope
- `available_local_partial`
