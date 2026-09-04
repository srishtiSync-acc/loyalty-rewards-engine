from .models import SafeMemberView
from .store import InMemoryStore


def lookup_member(store: InMemoryStore, member_id: str) -> SafeMemberView | None:
    member = store.get_member(member_id)
    if member is None:
        return None
    return SafeMemberView(
        member_id=member.member_id, display_name=member.display_name,
        tier_code=member.tier_code, points_balance=member.points_balance,
        lifetime_points=member.lifetime_points,
    )
