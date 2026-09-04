import copy
import json
from pathlib import Path

from pydantic import ValidationError

from .models import AuditEvent, Dataset, Member, Redemption, RulesConfiguration


class DataLoadError(ValueError):
    pass


def load_dataset(path: str | Path) -> Dataset:
    try:
        with Path(path).open(encoding="utf-8") as stream:
            return Dataset.model_validate(json.load(stream))
    except (OSError, json.JSONDecodeError, ValidationError, ValueError) as exc:
        raise DataLoadError(f"invalid loyalty dataset: {path}") from exc


class InMemoryStore:
    def __init__(self, members: list[Member], rules: RulesConfiguration):
        self._members = {member.member_id: copy.deepcopy(member) for member in members}
        self.rules = copy.deepcopy(rules)
        self.redemptions: dict[str, Redemption] = {}
        self.audit_events: list[AuditEvent] = []

    def get_member(self, member_id: str) -> Member | None:
        member = self._members.get(member_id)
        return copy.deepcopy(member) if member else None

    def save_member(self, member: Member) -> None:
        self._members[member.member_id] = copy.deepcopy(member)

    def save_redemption(self, redemption: Redemption) -> None:
        self.redemptions[redemption.redemption_id] = copy.deepcopy(redemption)

    def get_redemption(self, redemption_id: str) -> Redemption | None:
        redemption = self.redemptions.get(redemption_id)
        return copy.deepcopy(redemption) if redemption else None

    def add_audit(self, event: AuditEvent) -> None:
        self.audit_events.append(copy.deepcopy(event))

    def member_audit(self, member_id: str) -> list[AuditEvent]:
        return [copy.deepcopy(event) for event in self.audit_events if event.member_id == member_id]
