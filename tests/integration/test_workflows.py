from decimal import Decimal

from loyalty_rewards.adapters import lookup_member
from loyalty_rewards.models import Activity, ActivityType, Operation, Outcome


def test_earn_redeem_approval_and_safe_lookup(engine, member):
    view = lookup_member(engine.store, member.member_id)
    assert view is not None
    assert "email" not in view.model_dump()

    earned = engine.earn(member.member_id, Activity(
        event_id="earn-1", member_id=member.member_id,
        activity_type=ActivityType.ROOM, usd_amount=Decimal("100")))
    assert earned.outcome is Outcome.COMMITTED
    assert earned.points_awarded == 2500
    assert earned.audit_event.operation is Operation.EARN

    low = engine.redeem(member.member_id, "AWARD_NIGHT")
    assert low.outcome is Outcome.COMMITTED
    assert engine.store.get_member(member.member_id).points_balance == 30000

    high_member = member.model_copy(update={"member_id": "high-member", "points_balance": 40000})
    engine.store.save_member(high_member)
    high = engine.redeem(high_member.member_id, "SUITE")
    assert high.outcome is Outcome.PENDING_APPROVAL
    assert engine.store.get_member(high_member.member_id).points_balance == 40000
    approved = engine.approve_redemption(high.redemption_id)
    assert approved.outcome is Outcome.COMMITTED
    assert engine.store.get_member(high_member.member_id).points_balance == 0
    duplicate = engine.approve_redemption(high.redemption_id)
    assert duplicate.outcome is Outcome.COMMITTED
    assert engine.store.get_member(high_member.member_id).points_balance == 0


def test_rejected_redemption_preserves_balance(engine, member):
    before = member.points_balance
    result = engine.redeem(member.member_id, "SUITE")
    assert result.outcome is Outcome.PENDING_APPROVAL
    rejected = engine.reject_redemption(result.redemption_id)
    assert rejected.outcome is Outcome.REJECTED
    assert engine.store.get_member(member.member_id).points_balance == before


def test_tier_recalculation_changes_only_tier(engine, member):
    before = member.points_balance
    result = engine.recalc_tier(member.member_id)
    assert result.new_tier == "GOLD"
    assert engine.store.get_member(member.member_id).points_balance == before
