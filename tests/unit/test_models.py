from decimal import Decimal

import pytest
from pydantic import ValidationError

from loyalty_rewards.models import Activity, ActivityType, Member


def test_member_rejects_negative_balance():
    with pytest.raises(ValidationError):
        Member(member_id="m", tier_code="SILVER", points_balance=-1, lifetime_points=0)


def test_activity_requires_positive_amount():
    with pytest.raises(ValidationError):
        Activity(event_id="e", member_id="m", activity_type=ActivityType.ROOM, usd_amount=Decimal("0"))
