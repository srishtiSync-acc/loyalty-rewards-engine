# External Adapter Contracts

## Tier-Recalculation Agent

The custom agent at `.github/agents/tier-recalculation.agent.md` is an orchestration and explanation
surface, not a rules implementation.

Validation is local and runtime-free. A static contract test reads the instruction file and verifies
that it names the deterministic rules engine as source of truth, delegates to `recalc_tier()`,
does not invent thresholds or multipliers, does not directly mutate points balances, and protects
PII. A separate mocked delegation test supplies a fake or spy `recalc_tier()` callable and verifies
that a test-only representation of the intended agent workflow delegates to that callable rather
than implementing tier logic. The test-only harness is not a production adapter and adds no
runtime infrastructure.
Neither test invokes a hosted LLM, GitHub Copilot runtime, cloud service, or network dependency.

Inputs: member identifier and an optional request to explain the current/recalculated tier.

Allowed behavior:

- Retrieve the member through the safe member projection.
- Invoke `recalc_tier` from the deterministic engine.
- Explain the returned tier, lifetime points, and configured threshold in concise terms.

Forbidden behavior:

- Inventing thresholds or multipliers.
- Recalculating a tier independently.
- Directly modifying points balance.
- Revealing email or unnecessary PII.

## Optional MCP Member Lookup

Tool name: `lookup_member`

Input:

```json
{"member_id": "member-123"}
```

Success response shape:

```json
{
  "member_id": "member-123",
  "display_name": "Example Member",
  "tier_code": "GOLD",
  "points_balance": 42500,
  "lifetime_points": 75000
}
```

The exact response may omit fields not needed for the caller. It MUST NOT include `email` or
unnecessary PII. Unknown members return a controlled not-found result. The adapter reads the local
store and contains no earning, promotion, redemption, or tier business-rule implementation.

MCP is optional: the project remains fully functional and all acceptance criteria pass if this
adapter is omitted.
