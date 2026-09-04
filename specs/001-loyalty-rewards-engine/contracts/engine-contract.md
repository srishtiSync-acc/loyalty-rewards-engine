# Engine Contract

## Purpose

This contract describes the implementation-facing behavior of the deterministic rules engine. It
is language-neutral at the behavior level; Python and Pydantic type choices belong to the plan and
implementation tasks.

## Operations

### `earn(member_id, activity) -> EarnResult`

- Validates member, activity, and rules configuration.
- Calculates points with Decimal arithmetic using `points = usd_amount * 10 *
  tier_earn_multiplier * applicable_promotion_multiplier(s)`. USD amounts MAY contain fractional
  cents. The final result is rounded once to an integer with `ROUND_HALF_UP`; no intermediate
  multiplier result is rounded.
- Applies configured eligible promotions exactly according to event-scoped stackability.
- On success, updates balance and lifetime points and emits one auditable `EARN` mutation event.
- On failure, returns a controlled rejection and leaves state unchanged.

### `apply_promotions(activity, member, rules) -> PromotionResult`

- Pure calculation over supplied values.
- Returns eligible promotion IDs, applied modifiers, final multiplier/points, and explanation.
- Uses stable configuration order and does not mutate member state.

### `redeem(member_id, reward_code) -> RedemptionResult`

- Resolves reward cost from rules configuration.
- Rejects invalid or insufficient requests without mutation.
- Returns `PENDING_APPROVAL` without deduction when cost is above `human_gate_redeem_over`.
- Commits eligible low-value requests with a negative balance delta and `REDEEM` event.

### `approve_redemption(redemption_id) -> RedemptionResult`

- Accepts only a pending redemption.
- Commits once, deducts points, and records approval plus the successful `REDEEM` mutation.
- Duplicate approval or already-finalized requests do not deduct again.

### `reject_redemption(redemption_id) -> RedemptionResult`

- Accepts only a pending redemption.
- Marks it rejected, records the approval decision, and leaves points unchanged.

### `recalc_tier(member_id) -> TierResult`

- Purely determines the tier from lifetime points and configured thresholds, then updates the
  member tier when required.
- Does not change points balance.
- Returns old tier, new tier, threshold used, and explanation. Agent callers use this result.

### `audit_log(member_id, ...) -> list[AuditEvent]`

- Returns audit records for the member using safe fields.
- Must not expose email or unnecessary PII.

## Error and State Contract

Errors are explicit typed outcomes or controlled exceptions. No failed or pending operation may
change `points_balance`. A committed mutation must include before/after balances, signed delta,
operation, reason, member ID, and correlation ID.
