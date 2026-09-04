from loyalty_rewards.adapters import lookup_member


def test_safe_projection_excludes_private_email(store, member):
    view = lookup_member(store, member.member_id)
    assert view.model_dump() == {
        "member_id": member.member_id, "display_name": member.display_name,
        "tier_code": member.tier_code, "points_balance": member.points_balance,
        "lifetime_points": member.lifetime_points,
    }
    assert lookup_member(store, "missing") is None
