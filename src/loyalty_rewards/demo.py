import json
from pathlib import Path
from decimal import Decimal

from .adapters import lookup_member
from .engine import LoyaltyEngine
from .models import Activity, ActivityType
from .store import InMemoryStore, load_dataset


def main() -> None:
    dataset = load_dataset(Path(__file__).parents[2] / "data" / "members.json")
    engine = LoyaltyEngine(InMemoryStore(dataset.members, dataset.rules))
    member_id = dataset.members[0].member_id
    print("SAFE LOOKUP", lookup_member(engine.store, member_id).model_dump())
    earned = engine.earn(member_id, Activity(event_id="demo-earn", member_id=member_id,
                                              activity_type=ActivityType.ROOM,
                                              usd_amount=Decimal("100")))
    print("EARN", earned.model_dump(mode="json"))
    award = engine.redeem(member_id, "AWARD_NIGHT")
    print("REDEEM", award.model_dump(mode="json"))
    high_member = dataset.members[0].model_copy(update={"member_id": "demo-high-value", "points_balance": 40000})
    engine.store.save_member(high_member)
    suite = engine.redeem(high_member.member_id, "SUITE")
    print("PENDING", suite.model_dump(mode="json"))
    print("APPROVED", engine.approve_redemption(suite.redemption_id).model_dump(mode="json"))
    print("TIER", engine.recalc_tier(member_id).model_dump(mode="json"))
    print("AUDIT", [event.model_dump(mode="json") for event in engine.audit_log(member_id)])


if __name__ == "__main__":
    main()
