from decimal import Decimal

import pytest

from loyalty_rewards.models import Activity, ActivityType
from loyalty_rewards.rules import apply_promotions, calculate_base_points, calculate_tier


def test_gold_base_points_are_1250(activity, member, rules):
    assert calculate_base_points(activity, member, rules) == 1250


def test_fractional_points_round_once_half_up(member, rules):
    activity = Activity(event_id="fraction", member_id=member.member_id,
                        activity_type=ActivityType.FLIGHT, usd_amount=Decimal("0.1"))
    assert calculate_base_points(activity, member, rules) == 1


def test_promotion_applies_once_and_is_deterministic(activity, member, rules):
    first = apply_promotions(activity, member, rules)
    second = apply_promotions(activity, member, rules)
    assert first == second
    assert first.applied_promotion_ids == ["ROOM-BONUS"]
    assert first.final_points == 2500


def test_invalid_activity_is_rejected_without_state_change(member, rules):
    with pytest.raises(ValueError):
        Activity(event_id="bad", member_id=member.member_id,
                 activity_type=ActivityType.FLIGHT, usd_amount=Decimal("-1"))
