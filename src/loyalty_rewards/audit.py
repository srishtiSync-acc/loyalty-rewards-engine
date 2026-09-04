from typing import Any
from uuid import uuid4

from .models import AuditEvent, Operation, Outcome


def build_audit_event(member_id: str, operation: Operation, points_delta: int,
                      balance_before: int, balance_after: int, reason: str,
                      outcome: Outcome | str, correlation_id: str | None = None,
                      rule_context: dict[str, Any] | None = None) -> AuditEvent:
    return AuditEvent(
        transaction_id=str(uuid4()), member_id=member_id, operation=operation,
        points_delta=points_delta, balance_before=balance_before,
        balance_after=balance_after, reason=reason, outcome=outcome,
        correlation_id=correlation_id or str(uuid4()),
        rule_context=rule_context or {},
    )


def safe_audit_dict(event: AuditEvent) -> dict[str, Any]:
    return event.model_dump(mode="json")
