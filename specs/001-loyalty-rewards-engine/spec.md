# Feature Specification: Loyalty & Rewards Engine

**Feature Branch**: `001-loyalty-rewards-engine`

**Created**: 2026-09-04

**Status**: Draft

**Input**: User description: "Create the product specification for the deterministic, auditable Loyalty & Rewards Engine described in the project brief."

## Problem Statement

Developers need a lightweight loyalty and rewards rules engine that produces consistent points,
promotion, redemption, and tier outcomes. The engine must make every balance change explainable
and auditable while preventing agents or interfaces from inventing financial or loyalty rules.
The project must be demonstrable locally within a two-hour capstone implementation window.

## Goals

- Provide deterministic management of members, tiers, earning, promotions, redemptions,
  transactions, and tier recalculation.
- Make successful points mutations auditable and failed operations state-preserving.
- Require human approval for configured high-value redemptions.
- Allow agents and member lookup tools to orchestrate and explain operations without becoming
  a second source of business truth.
- Demonstrate the complete core workflow locally without cloud infrastructure or enterprise
  services.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Earn Points From Eligible Activity (Priority: P1)

A developer or loyalty workflow submits an eligible room-stay or flight activity for a member.
The engine calculates base points using the member tier, applies eligible promotions, updates the
balance, and returns an audit record describing the successful mutation.

**Why this priority**: Earning is the primary source of member points and establishes the
engine's determinism, promotion, balance, and audit foundations.

**Independent Test**: Submit a GOLD member's 100 USD eligible activity and verify the calculated
base points, final balance change, promotion result, and audit record without redemption or agents.

**Acceptance Scenarios**:

1. **Given** a GOLD member with a 1.25 earn multiplier, **When** 100 USD of eligible activity is
   earned, **Then** base points equal 100 x 10 x 1.25 = 1250 before promotions.
2. **Given** an active eligible EARN_MULTIPLIER promotion, **When** the activity is processed,
   **Then** the configured promotion is applied according to its stackability rules and the
   resulting balance mutation is auditable.
3. **Given** identical member state, activity, promotions, and rules, **When** earning is repeated,
   **Then** the result and audit-relevant calculation outcome are identical.

---

### User Story 2 - Redeem Rewards Safely (Priority: P1)

A member or authorized workflow requests an award-night or suite redemption. The engine verifies
availability of points, applies the configured high-value approval gate when required, and commits
only approved valid redemptions with an auditable REDEEM transaction.

**Why this priority**: Redemption changes member balances and therefore requires the strongest
state, approval, and audit guarantees.

**Independent Test**: Exercise successful, insufficient-balance, pending-approval, approved, and
rejected high-value redemptions and compare balances and transaction records after each outcome.

**Acceptance Scenarios**:

1. **Given** a balance of 42500 points, **When** a 15000-point award-night redemption is committed,
   **Then** the balance becomes 27500 and a REDEEM transaction is recorded.
2. **Given** a balance lower than the requested award cost, **When** redemption is requested,
   **Then** it is rejected with insufficient-balance and the balance is unchanged.
3. **Given** a redemption cost greater than the configured 30000-point threshold, **When** it is
   requested, **Then** it enters pending approval and points are not deducted.
4. **Given** a pending high-value redemption, **When** explicit human approval is recorded,
   **Then** the redemption commits, deducts points, and records the approval and balance mutation.
5. **Given** a pending high-value redemption, **When** explicit human rejection is recorded,
   **Then** the redemption is rejected and the balance is unchanged.

---

### User Story 3 - Recalculate Member Tier (Priority: P1)

A developer or tier-recalculation workflow evaluates a member's lifetime points against configured
tier thresholds. The engine returns the appropriate tier and updates tier state when the member
crosses a threshold.

**Why this priority**: Tier state controls future earning and must remain independent of agent
judgment.

**Independent Test**: Recalculate members below, at, and above configured thresholds and verify the
same lifetime-point inputs always produce the same tier outcomes.

**Acceptance Scenarios**:

1. **Given** lifetime points crossing a configured tier threshold, **When** tier recalculation is
   requested, **Then** the member is upgraded to the appropriate tier.
2. **Given** unchanged lifetime points and tier configuration, **When** recalculation is repeated,
   **Then** the result is unchanged.
3. **Given** a Tier-Recalculation Agent request, **When** the agent explains a tier change,
   **Then** it uses the deterministic engine result and does not invent thresholds or multipliers.

---

### User Story 4 - Inspect Members Without Exposing PII (Priority: P2)

A developer uses the member lookup capability to retrieve the minimum member information needed
for a workflow. The lookup response supports local demonstrations while excluding email addresses
and unnecessary personally identifiable information.

**Why this priority**: Safe lookup enables agent and MCP demonstrations without weakening privacy.

**Independent Test**: Look up a known member and verify that required operational fields are present
and email and unnecessary PII are absent from the response, logs, and demonstration output.

**Acceptance Scenarios**:

1. **Given** a member identifier in the project dataset, **When** lookup is requested, **Then** the
   response includes only the minimum fields needed for the requested operation.
2. **Given** a lookup or agent response, **When** it is inspected, **Then** member email and
   unnecessary PII are not exposed.

---

### User Story 5 - Demonstrate the Complete Local Workflow (Priority: P2)

A developer runs the project locally and demonstrates earning, promotion application, redemption,
insufficient-balance rejection, high-value approval, tier recalculation, audit history, the custom
Tier-Recalculation Agent, and member lookup when implemented.

**Why this priority**: Local demonstrability validates the capstone's value without requiring cloud
or enterprise dependencies.

**Independent Test**: Run the documented local demonstration and observe each required workflow
outcome and its corresponding audit evidence.

**Acceptance Scenarios**:

1. **Given** a local project checkout, **When** the developer runs the demonstration and tests,
   **Then** all required workflows complete without cloud infrastructure.

### Edge Cases

- An earning activity with an unsupported activity type or invalid monetary amount is rejected
  without changing the balance.
- A fractional final points result is rounded once with `ROUND_HALF_UP`; repeated evaluation of
  the same Decimal inputs produces the same integer result.
- A promotion that is inactive, ineligible, or outside its configured applicability is not applied.
- A non-stackable promotion is not applied more than once to one earning event, even if the event
  is evaluated repeatedly within that operation.
- Multiple eligible promotions are applied only when their configured stackability rules allow it.
- A redemption for an unknown reward or non-positive cost is rejected without a balance mutation.
- An insufficient-balance redemption is rejected without creating a successful REDEEM transaction.
- A high-value redemption remains pending until an explicit approval or rejection decision exists.
- Duplicate approval, rejection, or commit attempts do not deduct points more than once.
- A member at exactly a tier threshold receives the tier defined by the configured boundary rule.
- A member below every configured threshold remains in the lowest applicable tier.
- Missing or contradictory rules configuration prevents a business operation from silently using
  fallback values.
- Lookup of an unknown member returns a controlled not-found outcome without exposing unrelated
  member data.
- Audit records remain understandable without including unnecessary email addresses or PII.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST represent members with a points balance, lifetime points, and a
  configured loyalty tier.
- **FR-002**: The system MUST accept eligible room-stay and flight activities for points earning.
- **FR-003**: The system MUST calculate points with Decimal arithmetic as USD amount multiplied by
  10 points per USD, the applicable tier earn multiplier, and all applicable promotion multipliers.
  USD inputs MAY contain cents or other fractional values. The final calculated points MUST be
  rounded once to the nearest whole point using `ROUND_HALF_UP`; intermediate multipliers MUST NOT
  be rounded independently.
- **FR-004**: The system MUST apply active promotions only when configured eligibility rules match
  the earning activity and member context.
- **FR-005**: The system MUST support EARN_MULTIPLIER promotions and explicit stackable or
  non-stackable behavior.
- **FR-006**: The system MUST prevent a non-stackable promotion from being applied more than once
  to the same earning event.
- **FR-007**: The system MUST update points balance and lifetime points for successful earning
  operations according to the configured rules.
- **FR-008**: The system MUST support award-night redemption at 15000 points and suite redemption
  at 40000 points.
- **FR-009**: The system MUST reject insufficient-balance redemptions without changing the balance.
- **FR-010**: The system MUST create a REDEEM transaction for every successful redemption.
- **FR-011**: The system MUST obtain the `human_gate_redeem_over` value from rules configuration;
  the configured project value MUST be 30000 points.
- **FR-012**: The system MUST place redemptions above the configured threshold into a pending-
  approval state before deducting points.
- **FR-013**: The system MUST commit a pending high-value redemption only after explicit human
  approval and MUST reject it without mutation after explicit human rejection.
- **FR-014**: The system MUST determine tier from lifetime points and configured tier thresholds.
- **FR-015**: The system MUST provide tier recalculation independently of LLM or agent judgment.
- **FR-016**: The Tier-Recalculation Agent MUST be defined by the GitHub Copilot custom-agent
  instruction file `.github/agents/tier-recalculation.agent.md`. The instruction file MUST direct
  the agent to delegate tier calculation to the deterministic `recalc_tier()` function, treat the
  rules engine as the source of truth, avoid inventing thresholds or multipliers, avoid directly
  modifying points balances, and exclude unnecessary PII. Pytest validation MUST use static
  instruction-file contract checks and a mocked delegation test; it MUST NOT require a hosted LLM,
  Copilot runtime, or cloud service.
- **FR-017**: The system MUST create an auditable transaction or event for every successful points
  balance mutation, including earning and redemption.
- **FR-018**: Audit records MUST identify the member, operation, amount changed, reason, outcome,
  and relevant rule or promotion context without unnecessary PII.
- **FR-019**: Failed, rejected, and pending operations MUST NOT silently mutate points balance.
- **FR-020**: The system MUST provide a member lookup capability when feasible within project scope,
  returning only the minimum non-sensitive information needed for the operation.
- **FR-021**: Member lookup, agent responses, MCP responses, logs, and demonstrations MUST exclude
  email addresses and unnecessary PII.
- **FR-022**: The rules engine MUST remain the source of truth for earning, promotions, redemption,
  and tier calculation; surrounding agents and lookup tools MUST NOT contain conflicting rules.
- **FR-023**: Given identical member state, activity, promotion configuration, and rules
  configuration, the system MUST produce the same result.
- **FR-024**: The project MUST provide automated pytest coverage for AC-1 through AC-6 below.
- **FR-025**: The project MUST remain locally demonstrable without cloud infrastructure,
  authentication systems, web applications, databases, or enterprise services unless a planning
  decision shows one is essential to a stated requirement.

### Business Rules

- Points equal eligible USD amount x 10 x the applicable tier earn multiplier x all applicable
  promotion multipliers. USD and multipliers MUST use Decimal arithmetic rather than binary
  floating-point arithmetic.
- Final calculated points MUST be an integer rounded once to the nearest whole point using
  `ROUND_HALF_UP`; no intermediate multiplier result may be rounded independently.
- GOLD with a 1.25 multiplier earns 1250 base points from 100 USD before promotions.
- Award-night costs 15000 points; suite costs 40000 points.
- `human_gate_redeem_over` is a configured rule with project value 30000 points.
- A redemption above the threshold requires approval before deduction or commitment.
- Active promotions apply only when eligibility and stackability rules permit them.
- A non-stackable promotion applies at most once per earning event.
- Lifetime points and configured thresholds determine tier; agents do not determine tier.
- Successful point mutations require an auditable transaction or event.
- Failed, rejected, and pending operations do not silently change balances.

### Governance and Security Requirements

- Requirements, tasks, tests, and acceptance criteria MUST remain traceable through Spec Kit
  artifacts.
- The implementation MUST comply with the project constitution, especially deterministic rules,
  auditability, no silent balance changes, human approval, separation of agents, privacy, and
  testability.
- Business-critical calculations and security or points-rule enforcement MUST NOT rely on LLM
  judgment.
- Interfaces MUST minimize member data and MUST prevent unnecessary PII from appearing in output,
  MCP responses, logs, or demonstrations.
- Any scope reduction, including omission of member lookup if infeasible, MUST be documented in
  the plan and must preserve the deterministic rules and audit guarantees.

### Acceptance Criteria

- **AC-1**: Given a GOLD member, when `earn(100 USD)` is executed, base points equal
  `100 x 10 x 1.25 = 1250` before promotions. Fractional USD and multiplier inputs MUST use
  Decimal arithmetic and the final points result MUST be rounded once with `ROUND_HALF_UP`.
- **AC-2**: Given an active EARN_MULTIPLIER promotion on ROOM, when earning on a room stay, the
  multiplier is applied once and non-stackable promotions are not stacked.
- **AC-3**: Given a balance of 42500 points, when a 15000-point award-night redemption is
  committed, the balance becomes 27500 and a REDEEM transaction is recorded.
- **AC-4**: Given a balance lower than the award cost, when `redeem()` is called, the redemption is
  rejected with insufficient-balance and the balance is unchanged.
- **AC-5**: Given lifetime points crossing a tier threshold, when `recalc_tier()` is called, the
  member's tier is upgraded appropriately.
- **AC-6**: Given a redemption greater than 30000 points, when redemption is requested, explicit
  human approval is required before the redemption can be committed.

## Key Entities

- **Member**: A loyalty participant identified by a non-sensitive member identifier, current tier,
  points balance, and lifetime points.
- **Tier Rule**: A configured tier threshold and earn multiplier used to calculate tier and earning.
- **Activity**: An eligible room-stay or flight event with a USD amount and activity type.
- **Promotion**: A configured active or inactive earning modifier with eligibility, behavior, and
  stackability rules.
- **Reward**: A redeemable award-night or suite item with a configured points cost.
- **Redemption**: A requested reward exchange with status, approval state when applicable, and
  outcome.
- **Transaction or Audit Event**: An immutable record of a successful balance mutation or approval
  decision, including member, reason, change, and relevant rule context.
- **Rules Configuration**: The versioned configuration containing tier, promotion, reward, and
  human-approval rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of repeated evaluations using identical member state, activity, promotion
  configuration, and rules configuration produce identical business results in automated tests.
- **SC-002**: 100% of successful earning and redemption balance mutations in the acceptance test
  suite have a corresponding audit or transaction record.
- **SC-003**: 100% of rejected, failed, and pending redemption scenarios in the acceptance test
  suite leave the points balance unchanged until a valid commit occurs.
- **SC-004**: 100% of high-value redemption scenarios above 30000 points remain uncommitted until
  explicit approval is recorded.
- **SC-005**: All six mandatory acceptance criteria are represented by passing automated pytest
  tests before the feature is considered complete.
- **SC-006**: A developer can demonstrate earning, promotion, redemption, rejection, approval,
  tier recalculation, and audit history locally within 10 minutes using project documentation.
- **SC-007**: 100% of sampled agent, member lookup, MCP, log, and demonstration outputs exclude
  member email addresses and unnecessary PII.
- **SC-008**: At least 90% of first-time local demonstrators can complete the primary workflow
  without an undocumented setup step or cloud dependency.

## Assumptions

- The project brief's six acceptance criteria define the minimum automated test scope.
- Tier thresholds, tier multipliers, promotion definitions, reward costs, and approval threshold are
  supplied through rules configuration and can be represented in the project dataset.
- Member identifiers are sufficient for audit and lookup workflows; email is not required for the
  core operations.
- Local, in-memory or file-backed demonstration data is acceptable; durable production persistence
  is outside this capstone's scope.
- A human approval decision can be represented by an explicit local workflow action.
- If MCP member lookup cannot be completed within the two-hour capstone limit, the omission will be
  documented while preserving all core rules-engine and privacy requirements.
- No authentication, cloud deployment, web application, or external service is required for the
  initial local demonstration.

## Definition of Done

- All functional requirements and AC-1 through AC-6 are traceable to tests or documented test
  scenarios.
- All six mandatory acceptance tests pass, including base earning, promotion safety, successful
  redemption, insufficient balance, tier recalculation, and human approval gating.
- Successful balance mutations have auditable records, and failed or pending operations preserve
  the balance.
- Tier-Recalculation Agent behavior delegates to deterministic tier rules and cannot modify points.
- Member lookup, agent output, MCP output if implemented, logs, and demonstrations minimize PII.
- The local demonstration covers the required workflows and its setup is documented.
- The feature remains within the lightweight capstone scope with no unjustified infrastructure.
- Spec Kit artifacts preserve traceability from requirements through implementation tasks and tests.
