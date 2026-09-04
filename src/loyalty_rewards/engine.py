from uuid import uuid4

from .audit import build_audit_event
from .models import (
    Activity, ApprovalDecision, EarnResult, Member, Operation, Outcome,
    Redemption, RedemptionResult, TierResult,
)
from .rules import apply_promotions, calculate_tier, resolve_reward
from .store import InMemoryStore


class LoyaltyEngine:
    def __init__(self, store: InMemoryStore):
        self.store = store

    def apply_promotions(self, activity: Activity, member: Member | None = None):
        target = member or self.store.get_member(activity.member_id)
        if target is None:
            raise ValueError("member not found")
        return apply_promotions(activity, target, self.store.rules)

    def earn(self, member_id: str, activity: Activity) -> EarnResult:
        member = self.store.get_member(member_id)
        if member is None or activity.member_id != member_id:
            return EarnResult(outcome=Outcome.REJECTED, reason="member not found")
        try:
            result = apply_promotions(activity, member, self.store.rules)
        except ValueError as exc:
            return EarnResult(outcome=Outcome.REJECTED, reason=str(exc))
        before = member.points_balance
        member.points_balance += result.final_points
        member.lifetime_points += result.final_points
        self.store.save_member(member)
        event = build_audit_event(member_id, Operation.EARN, result.final_points, before,
                                  member.points_balance, "eligible activity earned", Outcome.COMMITTED,
                                  activity.event_id, {"base_points": result.base_points,
                                  "promotion_ids": result.applied_promotion_ids})
        self.store.add_audit(event)
        return EarnResult(outcome=Outcome.COMMITTED, points_awarded=result.final_points,
                          base_points=result.base_points, applied_promotion_ids=result.applied_promotion_ids,
                          reason=result.explanation, audit_event=event)

    def redeem(self, member_id: str, reward_code: str) -> RedemptionResult:
        member = self.store.get_member(member_id)
        if member is None:
            return RedemptionResult(outcome=Outcome.REJECTED, reward_code=reward_code, reason="member not found")
        try:
            cost = resolve_reward(reward_code, self.store.rules)
        except ValueError as exc:
            return RedemptionResult(outcome=Outcome.REJECTED, reward_code=reward_code, reason=str(exc))
        if member.points_balance < cost:
            return RedemptionResult(outcome=Outcome.REJECTED, reward_code=reward_code, points_cost=cost,
                                    reason="insufficient balance")
        redemption_id = str(uuid4())
        status = Outcome.PENDING_APPROVAL if cost > self.store.rules.human_gate_redeem_over else Outcome.COMMITTED
        redemption = Redemption(redemption_id=redemption_id, member_id=member_id, reward_code=reward_code,
                                points_cost=cost, status=status, reason="approval required" if status == Outcome.PENDING_APPROVAL else "committed")
        self.store.save_redemption(redemption)
        if status == Outcome.PENDING_APPROVAL:
            return RedemptionResult(outcome=status, redemption_id=redemption_id, reward_code=reward_code,
                                    points_cost=cost, reason=redemption.reason)
        return self._commit(redemption)

    def _commit(self, redemption: Redemption) -> RedemptionResult:
        member = self.store.get_member(redemption.member_id)
        if member is None:
            return RedemptionResult(outcome=Outcome.REJECTED, redemption_id=redemption.redemption_id,
                                    reward_code=redemption.reward_code, points_cost=redemption.points_cost, reason="member not found")
        before = member.points_balance
        member.points_balance -= redemption.points_cost
        self.store.save_member(member)
        event = build_audit_event(member.member_id, Operation.REDEEM, -redemption.points_cost, before,
                                  member.points_balance, "reward redeemed", Outcome.COMMITTED,
                                  redemption.redemption_id, {"reward_code": redemption.reward_code})
        self.store.add_audit(event)
        return RedemptionResult(outcome=Outcome.COMMITTED, redemption_id=redemption.redemption_id,
                                reward_code=redemption.reward_code, points_cost=redemption.points_cost,
                                reason="committed", audit_event=event)

    def approve_redemption(self, redemption_id: str) -> RedemptionResult:
        redemption = self.store.get_redemption(redemption_id)
        if redemption is None:
            return RedemptionResult(outcome=Outcome.REJECTED, reward_code="", reason="redemption not found")
        if redemption.status != Outcome.PENDING_APPROVAL:
            return RedemptionResult(outcome=redemption.status, redemption_id=redemption_id,
                                    reward_code=redemption.reward_code, points_cost=redemption.points_cost,
                                    reason="redemption already finalized")
        redemption.status = Outcome.COMMITTED
        redemption.approval_decision = ApprovalDecision.APPROVED
        redemption.reason = "approved"
        self.store.save_redemption(redemption)
        return self._commit(redemption)

    def reject_redemption(self, redemption_id: str) -> RedemptionResult:
        redemption = self.store.get_redemption(redemption_id)
        if redemption is None:
            return RedemptionResult(outcome=Outcome.REJECTED, reward_code="", reason="redemption not found")
        if redemption.status != Outcome.PENDING_APPROVAL:
            return RedemptionResult(outcome=redemption.status, redemption_id=redemption_id,
                                    reward_code=redemption.reward_code, points_cost=redemption.points_cost,
                                    reason="redemption already finalized")
        redemption.status = Outcome.REJECTED
        redemption.approval_decision = ApprovalDecision.REJECTED
        redemption.reason = "rejected by human approval"
        self.store.save_redemption(redemption)
        return RedemptionResult(outcome=Outcome.REJECTED, redemption_id=redemption_id,
                                reward_code=redemption.reward_code, points_cost=redemption.points_cost,
                                reason=redemption.reason)

    def recalc_tier(self, member_id: str) -> TierResult:
        member = self.store.get_member(member_id)
        if member is None:
            raise ValueError("member not found")
        old_tier = member.tier_code
        selected = calculate_tier(member.lifetime_points, self.store.rules.tier_rules)
        member.tier_code = selected.code
        self.store.save_member(member)
        return TierResult(member_id=member_id, old_tier=old_tier, new_tier=selected.code,
                          lifetime_points=member.lifetime_points, threshold_used=selected.lifetime_threshold,
                          explanation=f"{member.lifetime_points} lifetime points selects {selected.code}.")

    def audit_log(self, member_id: str):
        return self.store.member_audit(member_id)
