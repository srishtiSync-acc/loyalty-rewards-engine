# Data Model: Loyalty & Rewards Engine

## Overview

The model separates validated domain data from mutable operation state. Pydantic v2 models define
input/output boundaries; pure rules receive immutable-like model values and return calculation
results. The store owns current member state and the audit collection.

## Entities

### Member

- `member_id`: non-sensitive stable identifier; required and unique.
- `display_name`: optional safe display label; must not contain email by default.
- `tier_code`: configured tier identifier.
- `points_balance`: non-negative integer spendable points.
- `lifetime_points`: non-negative integer earned lifetime points.
- `email`: dataset-only field, never included in safe projections, logs, or agent/MCP responses.

Relationships: references one current TierRule; owns many transactions/audit events by `member_id`.

### TierRule

- `code`: stable tier identifier such as `SILVER` or `GOLD`.
- `lifetime_threshold`: non-negative integer boundary.
- `earn_multiplier`: positive Decimal multiplier; calculations MUST preserve Decimal precision.

Validation: thresholds are ordered and unambiguous in RulesConfiguration; boundary semantics are
inclusive at the selected tier threshold.

### Activity

- `event_id`: stable earning-event identifier for idempotent promotion evaluation.
- `member_id`: target member.
- `activity_type`: configured eligible type, initially `ROOM` or `FLIGHT`.
- `usd_amount`: positive Decimal amount that MAY contain cents or other fractional values.

Validation: unsupported activity types and non-positive amounts are rejected before mutation.

### Promotion

- `promotion_id`: stable identifier.
- `active`: whether the rule can apply.
- `activity_types`: eligible activity types.
- `member_tiers`: optional tier restrictions.
- `behavior`: initially `EARN_MULTIPLIER`.
- `multiplier`: positive Decimal modifier; promotion calculations MUST preserve Decimal precision.
- `stackable`: whether it can coexist with other eligible promotions.

Validation: inactive or ineligible promotions do not apply; evaluation order is stable from
configuration; each promotion ID is applied at most once per event.

### Points Calculation Precision

The calculation uses Decimal arithmetic throughout:

`points = usd_amount x 10 x tier_earn_multiplier x applicable_promotion_multiplier(s)`

The final result MUST be rounded exactly once to an integer using `ROUND_HALF_UP`. No intermediate
multiplier result may be rounded independently. This rule applies to base points before promotions
and to the final awarded points after promotions.

### Reward

- `reward_code`: initially `AWARD_NIGHT` or `SUITE`.
- `points_cost`: positive integer.

Initial configured costs: award night 15000; suite 40000.

### RulesConfiguration

- `base_points_per_usd`: 10.
- `human_gate_redeem_over`: 30000.
- `tier_rules`: ordered tier thresholds and multipliers.
- `promotion_rules`: configured promotions.
- `reward_rules`: configured reward costs.
- `eligible_activity_types`: configured activity types.

Validation: all required rules exist, thresholds are unambiguous, multipliers are positive, and
there are no contradictory reward or promotion identifiers.

### Redemption

- `redemption_id`: stable operation identifier.
- `member_id`: target member.
- `reward_code`: requested reward.
- `points_cost`: copied from validated reward rule at request time.
- `status`: `PENDING_APPROVAL`, `COMMITTED`, or `REJECTED`.
- `approval_decision`: absent, `APPROVED`, or `REJECTED` as applicable.
- `reason`: controlled outcome/rejection reason.

State transitions:

```text
requested -> COMMITTED       (cost <= threshold and balance sufficient)
requested -> PENDING_APPROVAL (cost > threshold and balance sufficient)
requested -> REJECTED         (unknown reward, invalid request, or insufficient balance)
PENDING_APPROVAL -> COMMITTED (explicit APPROVED decision)
PENDING_APPROVAL -> REJECTED  (explicit REJECTED decision)
```

A transition to `COMMITTED` is the only redemption transition that deducts points and creates a
successful `REDEEM` transaction. Pending and rejected states do not mutate the balance.

### Transaction / AuditEvent

- `transaction_id`: stable identifier.
- `member_id`: non-sensitive member identifier.
- `operation`: `EARN`, `REDEEM`, `TIER_RECALC`, or `APPROVAL`.
- `points_delta`: signed integer; balance mutations require non-zero delta.
- `balance_before`: integer snapshot.
- `balance_after`: integer snapshot.
- `reason`: human-readable controlled reason.
- `status`: operation outcome.
- `event_id` or `redemption_id`: correlation reference where applicable.
- `rule_context`: safe IDs/values needed to explain the result; no email or unnecessary PII.

Invariants: `balance_after = balance_before + points_delta`; every successful balance mutation has
one corresponding audit event; failed and pending operations have no successful mutation event.

### SafeMemberView

The lookup/agent projection contains only `member_id`, `display_name` if safe, `tier_code`,
`points_balance` when required, and `lifetime_points` when required. It excludes email and any
unnecessary PII.

## Module Ownership

- `models.py`: entity validation and enums.
- `rules.py`: pure calculations and eligibility decisions.
- `store.py`: JSON loading and mutable member/audit access.
- `audit.py`: immutable event construction and safe serialization.
- `engine.py`: explicit operations `earn`, `apply_promotions`, `redeem`, `recalc_tier`, and
  `audit_log` with mutation boundaries.
- `adapters.py`: SafeMemberView and optional MCP lookup projection.
