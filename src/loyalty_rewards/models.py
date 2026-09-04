from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ActivityType(str, Enum):
    ROOM = "ROOM"
    FLIGHT = "FLIGHT"


class PromotionBehavior(str, Enum):
    EARN_MULTIPLIER = "EARN_MULTIPLIER"


class Operation(str, Enum):
    EARN = "EARN"
    REDEEM = "REDEEM"
    TIER_RECALC = "TIER_RECALC"
    APPROVAL = "APPROVAL"


class Outcome(str, Enum):
    REJECTED = "REJECTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    COMMITTED = "COMMITTED"
    NOT_FOUND = "NOT_FOUND"


class ApprovalDecision(str, Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class Member(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    member_id: str = Field(min_length=1)
    display_name: str | None = None
    tier_code: str
    points_balance: int = Field(ge=0)
    lifetime_points: int = Field(ge=0)
    email: str | None = None


class TierRule(BaseModel):
    code: str = Field(min_length=1)
    lifetime_threshold: int = Field(ge=0)
    earn_multiplier: Decimal = Field(gt=0)


class Activity(BaseModel):
    event_id: str = Field(min_length=1)
    member_id: str = Field(min_length=1)
    activity_type: ActivityType
    usd_amount: Decimal = Field(gt=0)


class Promotion(BaseModel):
    promotion_id: str = Field(min_length=1)
    active: bool = True
    activity_types: list[ActivityType]
    member_tiers: list[str] | None = None
    behavior: PromotionBehavior = PromotionBehavior.EARN_MULTIPLIER
    multiplier: Decimal = Field(gt=0)
    stackable: bool = False


class Reward(BaseModel):
    reward_code: str = Field(min_length=1)
    points_cost: int = Field(gt=0)


class RulesConfiguration(BaseModel):
    base_points_per_usd: Decimal = Field(gt=0)
    human_gate_redeem_over: int = Field(ge=0)
    eligible_activity_types: list[ActivityType]
    tier_rules: list[TierRule] = Field(min_length=1)
    promotion_rules: list[Promotion] = []
    reward_rules: list[Reward] = Field(min_length=1)

    @model_validator(mode="after")
    def validate_unique_rules(self):
        if len({rule.code for rule in self.tier_rules}) != len(self.tier_rules):
            raise ValueError("tier identifiers must be unique")
        if len({rule.promotion_id for rule in self.promotion_rules}) != len(self.promotion_rules):
            raise ValueError("promotion identifiers must be unique")
        if len({rule.reward_code for rule in self.reward_rules}) != len(self.reward_rules):
            raise ValueError("reward identifiers must be unique")
        return self


class Redemption(BaseModel):
    redemption_id: str
    member_id: str
    reward_code: str
    points_cost: int = Field(gt=0)
    status: Outcome
    approval_decision: ApprovalDecision | None = None
    reason: str


class AuditEvent(BaseModel):
    transaction_id: str
    member_id: str
    operation: Operation
    points_delta: int
    balance_before: int = Field(ge=0)
    balance_after: int = Field(ge=0)
    reason: str
    outcome: Outcome | str
    correlation_id: str
    rule_context: dict[str, Any] = {}

    @model_validator(mode="after")
    def balance_invariant(self):
        if self.balance_after != self.balance_before + self.points_delta:
            raise ValueError("audit balance invariant violated")
        return self


class SafeMemberView(BaseModel):
    member_id: str
    display_name: str | None = None
    tier_code: str
    points_balance: int
    lifetime_points: int


class PromotionResult(BaseModel):
    base_points: int
    applied_promotion_ids: list[str]
    promotion_multiplier: Decimal
    final_points: int
    explanation: str


class EarnResult(BaseModel):
    outcome: Outcome
    points_awarded: int = 0
    base_points: int = 0
    applied_promotion_ids: list[str] = []
    reason: str
    audit_event: AuditEvent | None = None


class RedemptionResult(BaseModel):
    outcome: Outcome
    redemption_id: str | None = None
    reward_code: str
    points_cost: int | None = None
    reason: str
    audit_event: AuditEvent | None = None


class TierResult(BaseModel):
    outcome: Outcome = Outcome.COMMITTED
    member_id: str
    old_tier: str
    new_tier: str
    lifetime_points: int
    threshold_used: int
    explanation: str


class Dataset(BaseModel):
    members: list[Member]
    rules: RulesConfiguration
