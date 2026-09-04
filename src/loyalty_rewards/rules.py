from decimal import Decimal, ROUND_HALF_UP

from .models import Activity, Member, PromotionResult, RulesConfiguration, TierRule


def _round_points(value: Decimal) -> int:
    return int(value.quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def calculate_base_points(activity: Activity, member: Member, rules: RulesConfiguration) -> int:
    if activity.activity_type not in rules.eligible_activity_types:
        raise ValueError("unsupported activity type")
    tier = next((item for item in rules.tier_rules if item.code == member.tier_code), None)
    if tier is None:
        raise ValueError("member tier is not configured")
    return _round_points(activity.usd_amount * rules.base_points_per_usd * tier.earn_multiplier)


def apply_promotions(activity: Activity, member: Member, rules: RulesConfiguration) -> PromotionResult:
    base_points = calculate_base_points(activity, member, rules)
    multiplier = Decimal("1")
    applied: list[str] = []
    stackable_seen = False
    for promotion in rules.promotion_rules:
        if not promotion.active or activity.activity_type not in promotion.activity_types:
            continue
        if promotion.member_tiers and member.tier_code not in promotion.member_tiers:
            continue
        if not promotion.stackable and applied:
            continue
        if not promotion.stackable and promotion.promotion_id in applied:
            continue
        if not promotion.stackable and stackable_seen:
            continue
        multiplier *= promotion.multiplier
        applied.append(promotion.promotion_id)
        if not promotion.stackable:
            stackable_seen = True
    final_points = _round_points(Decimal(base_points) * multiplier)
    return PromotionResult(
        base_points=base_points, applied_promotion_ids=applied,
        promotion_multiplier=multiplier, final_points=final_points,
        explanation=f"Base points {base_points}; promotions {', '.join(applied) or 'none'}; final {final_points}.",
    )


def resolve_reward(reward_code: str, rules: RulesConfiguration) -> int:
    reward = next((item for item in rules.reward_rules if item.reward_code == reward_code), None)
    if reward is None:
        raise ValueError("unknown reward")
    return reward.points_cost


def calculate_tier(lifetime_points: int, tier_rules: list[TierRule]) -> TierRule:
    eligible = [rule for rule in tier_rules if lifetime_points >= rule.lifetime_threshold]
    if not eligible:
        return min(tier_rules, key=lambda rule: rule.lifetime_threshold)
    return max(eligible, key=lambda rule: rule.lifetime_threshold)
