import pytest

from loyalty_rewards.audit import build_audit_event, safe_audit_dict
from loyalty_rewards.models import Operation, Outcome


def test_audit_invariant_and_safe_serialization():
    event = build_audit_event("m", Operation.EARN, 10, 0, 10, "earned", Outcome.COMMITTED,
                              rule_context={"member_id": "m"})
    assert safe_audit_dict(event)["points_delta"] == 10
    assert "email" not in safe_audit_dict(event)
    with pytest.raises(ValueError):
        build_audit_event("m", Operation.EARN, 10, 0, 11, "bad", Outcome.COMMITTED)
