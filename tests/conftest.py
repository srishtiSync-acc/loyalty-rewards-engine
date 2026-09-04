from decimal import Decimal

import pytest

from loyalty_rewards.models import (
    Activity,
    ActivityType,
    Member,
    Promotion,
    Reward,
    RulesConfiguration,
    TierRule,
)
from loyalty_rewards.store import InMemoryStore
from loyalty_rewards.engine import LoyaltyEngine


@pytest.fixture
def rules():
    return RulesConfiguration(
        base_points_per_usd=Decimal("10"),
        human_gate_redeem_over=30000,
        eligible_activity_types=[ActivityType.ROOM, ActivityType.FLIGHT],
        tier_rules=[
            TierRule(code="SILVER", lifetime_threshold=0, earn_multiplier=Decimal("1")),
            TierRule(code="GOLD", lifetime_threshold=50000, earn_multiplier=Decimal("1.25")),
        ],
        promotion_rules=[
            Promotion(
                promotion_id="ROOM-BONUS", active=True,
                activity_types=[ActivityType.ROOM], member_tiers=["GOLD"],
                multiplier=Decimal("2"), stackable=False,
            )
        ],
        reward_rules=[
            Reward(reward_code="AWARD_NIGHT", points_cost=15000),
            Reward(reward_code="SUITE", points_cost=40000),
        ],
    )


@pytest.fixture
def member():
    return Member(
        member_id="member-123", display_name="Example Member", tier_code="GOLD",
        points_balance=42500, lifetime_points=75000, email="private@example.com",
    )


@pytest.fixture
def store(member, rules):
    return InMemoryStore([member], rules)


@pytest.fixture
def engine(store):
    return LoyaltyEngine(store)


@pytest.fixture
def activity():
    return Activity(
        event_id="event-1", member_id="member-123", activity_type=ActivityType.ROOM,
        usd_amount=Decimal("100"),
    )
