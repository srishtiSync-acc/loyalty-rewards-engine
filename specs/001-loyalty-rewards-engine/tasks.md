---

description: "Executable implementation tasks for the Loyalty & Rewards Engine"
---

# Tasks: Loyalty & Rewards Engine

**Input**: Design documents from `/specs/001-loyalty-rewards-engine/`

**Prerequisites**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md),
[data-model.md](data-model.md), [contracts/](contracts/), [quickstart.md](quickstart.md)

**Tests**: Included because the specification requires pytest coverage for AC-1 through AC-6 and
explicit edge-case coverage.

**Organization**: Tasks are grouped by user story. Mandatory core stories precede optional MCP work.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel after listed dependencies are complete and touches separate files.
- **[Story]**: User story label for story-phase tasks; setup, foundational, and polish tasks have no
  story label.
- Every task names the file or files it creates or changes.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize the lightweight Python package, local data layout, and test configuration.

- [X] T001 Create the Python package layout in `src/loyalty_rewards/`, `tests/unit/`,
  `tests/integration/`, `data/`, and `.github/agents/` according to `plan.md` (FR-025).
- [X] T002 Create `pyproject.toml` with Python 3.11+ metadata, Pydantic v2 runtime dependency,
  pytest development dependency, src-layout configuration, and a local demo entry point (FR-025).
- [X] T003 [P] Create `src/loyalty_rewards/__init__.py` with the public package surface reserved for
  the engine operations in the plan (FR-022).
- [X] T004 [P] Create `tests/conftest.py` with reusable isolated member, rules, and store fixtures
  for deterministic unit and integration tests (FR-024).
- [X] T005 Create `README.md` with project purpose, local Windows/VS Code prerequisites, and
  a placeholder map to the quickstart workflow (FR-025, SC-006).

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Establish validated domain models, local JSON data, state access, and audit primitives.

**Checkpoint**: No user-story implementation begins until these shared contracts and invariants are
available.

- [X] T006 Define Pydantic v2 enums and domain models in `src/loyalty_rewards/models.py` for
  Member, TierRule, Activity, Promotion, Reward, RulesConfiguration, Redemption, Transaction,
  AuditEvent, and SafeMemberView (FR-001, FR-018).
- [X] T007 [P] Add model validation tests in `tests/unit/test_models.py` for non-negative balances,
  positive amounts/costs/multipliers, supported activity types, unique identifiers, and safe
  lookup fields (FR-001, FR-002, FR-008, FR-021).
- [X] T008 Create the representative local dataset in `data/members.json` with GOLD multiplier 1.25,
  award-night 15000, suite 40000, `human_gate_redeem_over` 30000, tier thresholds, ROOM and
  FLIGHT activities, active EARN_MULTIPLIER promotion, and a member with private email data
  (FR-003, FR-008, FR-011, FR-021).
- [X] T009 Implement validated JSON loading in `src/loyalty_rewards/store.py`, including controlled
  errors for missing, malformed, contradictory, or invalid rules configuration (FR-001, FR-025).
- [X] T010 [P] Add store and dataset tests in `tests/unit/test_store.py` proving the dataset loads,
  required configured values are present, invalid JSON/configuration fails explicitly, and email is
  retained only in internal data (FR-011, FR-021).
- [X] T011 Implement in-memory member, rules, redemption, and audit state access in
  `src/loyalty_rewards/store.py` with copy/replace behavior that prevents accidental mutation
  during pure calculations (FR-019, FR-023).
- [X] T012 [P] Implement audit event construction and safe serialization in
  `src/loyalty_rewards/audit.py`, including member ID, operation, signed delta, before/after
  balances, reason, outcome, correlation ID, and safe rule context (FR-017, FR-018, FR-021).
- [X] T013 [P] Add audit primitive tests in `tests/unit/test_audit.py` for balance-delta invariants,
  required explanation fields, immutable/safe output, and exclusion of email and unnecessary PII
  (FR-017, FR-018, FR-021).
- [X] T014 Create shared error/result types and explicit operation outcome conventions in
  `src/loyalty_rewards/models.py` for rejected, pending, committed, and not-found outcomes
  without using silent fallback values (FR-009, FR-012, FR-019).

## Phase 3: User Story 1 - Earn Points and Apply Promotions (Priority: P1) 🎯 MVP

**Goal**: Calculate deterministic base points and configured promotions, mutate balance/lifetime
points only on success, and create an auditable EARN event.

**Independent Test**: Use a GOLD member and a ROOM activity to verify 1250 base points before
promotions, exactly-once promotion application, final balance/lifetime points, repeatability, and
an EARN audit event without redemption or agents.

### Tests for User Story 1

- [X] T015 [P] [US1] Add AC-1 unit test in `tests/unit/test_rules.py` proving GOLD 1.25 earning
  calculates `100 x 10 x 1.25 = 1250` base points before promotions (FR-003, AC-1).
- [X] T016 [P] [US1] Add AC-2 promotion tests in `tests/unit/test_promotions.py` proving an active
  ROOM EARN_MULTIPLIER applies once and a non-stackable promotion is not stacked (FR-004, FR-005,
  FR-006, AC-2).
- [X] T017 [P] [US1] Add deterministic repeated-calculation tests in `tests/unit/test_rules.py`
  proving identical member/activity/promotion/rules inputs return identical results (FR-023, SC-001).
- [X] T018 [P] [US1] Add earning edge-case tests in `tests/unit/test_rules.py` for unsupported
  activity, non-positive USD amount, inactive/ineligible promotion, and contradictory configuration
  proving failed operations leaving state unchanged. Include a fractional-points boundary case
  using Decimal USD and multiplier inputs to prove the final result is rounded once with
  ROUND_HALF_UP, with no intermediate rounding (FR-002, FR-003, FR-004, FR-019, FR-023).
- [X] T019 [US1] Add earning workflow integration tests in `tests/integration/test_earning.py` for
  successful balance and lifetime-point mutation plus one EARN audit event (FR-007, FR-017, SC-002).

### Implementation for User Story 1

- [X] T020 [P] [US1] Implement pure base-point calculation and earning validation in
  `src/loyalty_rewards/rules.py` using Decimal inputs, configured points-per-USD and tier
  multiplier, and one final ROUND_HALF_UP conversion to an integer (FR-002, FR-003, AC-1).
- [X] T021 [P] [US1] Implement pure promotion eligibility, stable ordering, multiplier application,
  and event-scoped non-stackable tracking in `src/loyalty_rewards/rules.py` (FR-004, FR-005,
  FR-006, AC-2).
- [X] T022 [US1] Implement `apply_promotions(activity, member, rules)` in
  `src/loyalty_rewards/engine.py` or the rules boundary defined by `contracts/engine-contract.md`
  as a non-mutating operation returning applied IDs and explanation (FR-004, FR-006).
- [X] T023 [US1] Implement `earn(member_id, activity)` in `src/loyalty_rewards/engine.py`, applying
  pure calculations first and mutating balance/lifetime points only after validation succeeds
  (FR-007, FR-019, AC-1, AC-2).
- [X] T024 [US1] Integrate `audit.py` with the successful earn path in
  `src/loyalty_rewards/engine.py` so every points mutation records before/after balances, delta,
  reason, promotion context, and member ID (FR-017, FR-018, SC-002).

**Checkpoint**: US1 is independently demonstrable with `pytest tests/unit/test_rules.py
 tests/unit/test_promotions.py tests/integration/test_earning.py` and no redemption dependency.

## Phase 4: User Story 2 - Redeem Rewards and Govern High-Value Approval (Priority: P1)

**Goal**: Support award-night and suite redemption, preserve state on rejection/pending outcomes,
and require explicit approval before high-value deduction.

**Independent Test**: Exercise successful award-night redemption, insufficient balance, pending
suite redemption, approved suite redemption, rejected suite redemption, duplicate decisions, and
corresponding audit records.

### Tests for User Story 2

- [X] T025 [P] [US2] Add AC-3 integration test in `tests/integration/test_redemption.py` proving
  42500 points minus 15000 commits to 27500 and creates a REDEEM transaction (FR-008, FR-010, AC-3).
- [X] T026 [P] [US2] Add AC-4 integration test in `tests/integration/test_redemption.py` proving
  insufficient balance returns the required rejection and leaves balance and successful audit
  mutations unchanged (FR-009, FR-019, AC-4).
- [X] T027 [P] [US2] Add AC-6 integration tests in `tests/integration/test_approval.py` proving a
  redemption over configured 30000 enters pending approval with no deduction and cannot commit
  until explicit approval (FR-011, FR-012, FR-013, AC-6, SC-004).
- [X] T028 [P] [US2] Add approval rejection and idempotency tests in `tests/integration/test_approval.py`
  proving explicit rejection preserves balance and duplicate approve/reject/commit attempts cannot
  deduct twice (FR-013, FR-019).
- [X] T029 [P] [US2] Add redemption edge-case tests in `tests/unit/test_redemption_rules.py` for
  unknown reward, non-positive cost, exact threshold boundary, and malformed configured threshold
  (FR-008, FR-011, FR-019).
- [X] T030 [US2] Add audit integration assertions in `tests/integration/test_redemption.py` and
  `tests/integration/test_approval.py` for successful REDEEM, approval decision, and no successful
  mutation event on rejected/pending operations (FR-017, FR-018, SC-002, SC-003).

### Implementation for User Story 2

- [X] T031 [P] [US2] Implement pure reward resolution, sufficient-balance validation, and
  threshold classification in `src/loyalty_rewards/rules.py` using configured reward costs and
  `human_gate_redeem_over` (FR-008, FR-009, FR-011).
- [X] T032 [US2] Implement `redeem(member_id, reward_code)` in `src/loyalty_rewards/engine.py`
  with explicit `REJECTED`, `PENDING_APPROVAL`, and `COMMITTED` results and no mutation before
  commit (FR-009, FR-012, FR-019, AC-4, AC-6).
- [X] T033 [US2] Implement `approve_redemption(redemption_id)` and
  `reject_redemption(redemption_id)` in `src/loyalty_rewards/engine.py` with one-way state
  transitions, explicit decisions, and duplicate-operation protection (FR-013, FR-019).
- [X] T034 [US2] Add committed redemption deduction and REDEEM audit transaction creation in
  `src/loyalty_rewards/engine.py` using the audit primitive and balance invariant (FR-010,
  FR-017, FR-018, AC-3).

**Checkpoint**: US2 is independently demonstrable with local members/rules and proves no balance
changes occur for insufficient, pending, or rejected redemptions.

## Phase 5: User Story 3 - Recalculate Tiers and Provide Tier Agent (Priority: P1)

**Goal**: Determine and update tiers from configured lifetime thresholds, and expose a custom agent
that delegates to the deterministic engine without inventing rules or modifying points.

**Independent Test**: Recalculate below, exactly at, and above tier thresholds, repeat unchanged
inputs, and invoke the custom agent against the same engine result.

### Tests for User Story 3

- [X] T035 [P] [US3] Add AC-5 tier boundary tests in `tests/unit/test_tiers.py` for below-threshold,
  exact-threshold, and above-threshold lifetime points selecting the configured tier (FR-014, AC-5).
- [X] T036 [P] [US3] Add deterministic tier repetition tests in `tests/unit/test_tiers.py` proving
  unchanged lifetime points and configuration return the same tier and explanation (FR-014, FR-015,
  FR-023, AC-5).
- [X] T037 [P] [US3] Add tier state integration tests in `tests/integration/test_tiers.py` proving
  recalc updates tier only, does not change points balance, and records any configured tier event
  safely (FR-014, FR-017, FR-019).
- [X] T038 [P] [US3] Add static custom-agent contract tests in
  `tests/integration/test_tier_agent.py` that read `.github/agents/tier-recalculation.agent.md`
  and verify source-of-truth delegation, no invented thresholds/multipliers, no direct balance
  mutation, and PII-safety instructions. In the same test module, add a mocked delegation test
  that uses a test-only workflow representation to spy on the deterministic `recalc_tier()`
  callable and prove delegation rather than independent tier logic; do not add a production agent
  runtime or invoke an LLM, Copilot runtime, cloud service, or network dependency (FR-015, FR-016,
  FR-021, FR-022).

### Implementation for User Story 3

- [X] T039 [US3] Implement pure `calculate_tier(lifetime_points, tier_rules)` in
  `src/loyalty_rewards/rules.py` with explicit configured boundary semantics and no agent dependency
  (FR-014, FR-015, AC-5).
- [X] T040 [US3] Implement `recalc_tier(member_id)` in `src/loyalty_rewards/engine.py`, updating
  only the member tier from the pure result and returning old/new tier, threshold, and explanation
  (FR-014, FR-015, FR-019).
- [X] T041 [US3] Create `.github/agents/tier-recalculation.agent.md` with instructions to retrieve
  safe member data, call deterministic tier recalculation, explain returned results, never invent
  thresholds/multipliers, and never mutate balances (FR-016, FR-022).

**Checkpoint**: US3 is independently testable with no LLM runtime; the agent file is only an
orchestration contract over `recalc_tier`.

## Phase 6: User Story 4 - Privacy-Safe Member Lookup (Priority: P2)

**Goal**: Return the minimum member information needed for local workflows while excluding email
and unnecessary PII from lookup, agent, MCP-shaped, log, and demonstration outputs.

**Independent Test**: Look up a known member and an unknown member, inspect serialized output, and
prove email is absent while required operational fields remain available.

### Tests for User Story 4

- [X] T042 [P] [US4] Add safe projection tests in `tests/unit/test_adapters.py` proving
  `SafeMemberView` excludes email and unnecessary PII while retaining required member ID, tier,
  balance, and lifetime points fields (FR-020, FR-021, AC privacy scenarios).
- [X] T043 [P] [US4] Add unknown-member and response-serialization tests in
  `tests/integration/test_member_lookup.py` for controlled not-found behavior and no private data
  leakage in JSON/text output (FR-020, FR-021).
- [X] T044 [P] [US4] Add log/demo privacy tests in `tests/integration/test_privacy.py` proving audit,
  agent-facing, and demonstration output does not contain member email or unnecessary PII (FR-018,
  FR-021, SC-007).

### Implementation for User Story 4

- [X] T045 [US4] Implement safe member projection and `lookup_member(member_id)` in
  `src/loyalty_rewards/adapters.py`, reading through the store and returning only SafeMemberView
  fields (FR-020, FR-021).
- [X] T046 [US4] Route audit and operation explanations through safe serialization in
  `src/loyalty_rewards/audit.py` and `src/loyalty_rewards/adapters.py`, preventing accidental email
  or raw-member dumps (FR-018, FR-021).

**Checkpoint**: US4 is independently testable against the local JSON dataset without MCP.

## Phase 7: User Story 5 - Local Demonstration and Documentation (Priority: P2)

**Goal**: Demonstrate all mandatory workflows locally in a short, documented run, including the
custom agent behavior and audit trail.

**Independent Test**: Follow README/quickstart commands from a clean Windows VS Code terminal and
observe earning, promotion, redemptions, approval, tier recalculation, safe lookup, and audit output.

### Tests for User Story 5

- [X] T047 [US5] Add an end-to-end demonstration test in `tests/integration/test_demo.py` that runs
  the local workflow and asserts earning, promotion, successful and rejected redemption, pending and
  approved high-value redemption, tier recalculation, audit output, and PII exclusion (FR-025,
  SC-006, SC-007).

### Implementation for User Story 5

- [X] T048 [US5] Implement `src/loyalty_rewards/demo.py` to load `data/members.json` and print the
  required workflow steps and safe outcomes without exposing email or unnecessary PII (FR-025,
  SC-006, SC-007).
- [X] T049 [US5] Update `README.md` with Windows PowerShell setup, pytest command, demo command,
  expected outcomes, architecture boundaries, and optional MCP status (FR-025, SC-006).
- [X] T050 [US5] Align `specs/001-loyalty-rewards-engine/quickstart.md` with the implemented local
  commands and document any intentionally omitted optional integration (SC-006, FR-025).

**Checkpoint**: The mandatory project is demonstrable locally without database, cloud, web frontend,
authentication service, or MCP dependency.

## Phase 8: Optional MCP Member Lookup (Priority: P2, only after mandatory work)

**Goal**: Add a thin MCP-shaped member lookup integration without duplicating business rules or
making it a core dependency. Omit this phase if the two-hour capstone limit is reached.

**Independent Test**: Invoke the lookup tool with a known and unknown member, verify safe response
shape and PII exclusion, then remove/disable the adapter and rerun all mandatory tests unchanged.

### Tests for Optional MCP

- [X] T051 [P] Add optional MCP contract tests in `tests/integration/test_mcp_lookup.py` for known and
  unknown members, safe fields, controlled errors, and no email/PII (FR-020, FR-021).
- [X] T052 [P] Add optional dependency-isolation test in `tests/integration/test_mcp_optional.py`
  proving mandatory engine tests pass when the MCP adapter is unavailable (FR-025, SC-005).

### Implementation for Optional MCP

- [X] T053 Implement the optional lookup tool adapter in `src/loyalty_rewards/adapters.py` or a
  dedicated `src/loyalty_rewards/mcp_lookup.py` using `lookup_member`, without business-rule logic
  or direct balance mutation (FR-020, FR-022).
- [X] T054 Document optional MCP setup, response schema, PII boundary, and omission fallback in
  `README.md` and `specs/001-loyalty-rewards-engine/contracts/external-adapters.md` (FR-020, FR-021).

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Run the complete quality gate, preserve traceability, and verify the two-hour scope.

- [X] T055 [P] Add coverage/traceability comments or test IDs in `tests/` mapping AC-1 through AC-6
  and core FRs to executable tests (FR-024, Constitution X).
- [X] T056 [P] Review all public result, audit, demo, agent, and optional adapter outputs for
  determinism, safe PII minimization, and absence of duplicated business rules (Constitution I,
  V, VIII).
- [X] T057 Run `python -m pytest` and the quickstart demonstration from `README.md`; fix only
  failures within the specified lightweight scope and record results in the implementation notes
  (SC-005, SC-006).
- [X] T058 Review `specs/001-loyalty-rewards-engine/plan.md`, `spec.md`, `data-model.md`,
  `contracts/`, `quickstart.md`, and `tasks.md` for requirement-to-task-to-test traceability
  before declaring the feature complete (FR-024, Constitution X).

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**: No dependencies; creates package/test/configuration paths.
- **Phase 2 Foundational**: Depends on T001-T005; blocks all user stories.
- **Phase 3 US1**: Depends on Phase 2; MVP and source of shared earn/audit conventions.
- **Phase 4 US2**: Depends on Phase 2 and the audit/store primitives; can proceed after foundation,
  but reuses no US1 behavior except shared models and audit.
- **Phase 5 US3**: Depends on Phase 2; can proceed in parallel with US1/US2 after foundation.
- **Phase 6 US4**: Depends on Phase 2; can proceed in parallel, with agent-safe serialization
  conventions from US3 if available.
- **Phase 7 US5**: Depends on US1, US2, US3, and US4 mandatory paths.
- **Phase 8 Optional MCP**: Depends on US4 and Phase 7; never blocks mandatory completion.
- **Phase 9 Polish**: Depends on all selected mandatory phases and optional MCP only if attempted.

### User Story Dependencies

- **US1 (P1)**: Depends on Foundational only; recommended MVP.
- **US2 (P1)**: Depends on Foundational only; shares models/store/audit but does not require US1.
- **US3 (P1)**: Depends on Foundational only; agent tests depend on engine tier operation.
- **US4 (P2)**: Depends on Foundational only; MCP is not required.
- **US5 (P2)**: Depends on completed mandatory US1-US4 flows.
- **Optional MCP**: Depends on US4; explicitly non-blocking.

### Parallel Execution Opportunities

After Phase 2, these groups can run in parallel when different contributors are available:

- US1 pure earning/promotions (`T015-T024`), US2 redemption/approval (`T025-T034`), and US3 tier
  logic (`T035-T041`) touch mostly separate rule/test slices.
- US4 safe lookup (`T042-T046`) can run alongside US1-US3 after shared models/store exist.
- Within US1, tests `T015-T019` can be drafted in parallel; implementations `T020-T021` can be
  drafted in parallel before orchestration `T022-T024`.
- Within US2, tests `T025-T030` can be drafted in parallel; pure rules `T031` can proceed before
  engine transitions `T032-T034`.
- Optional MCP tests and adapter tasks `T051-T054` are parallelizable only after US4 and must not
  delay the mandatory demo.

## Parallel Example: Core Stories After Foundation

```text
Task A: T015-T024 - US1 earning and promotion slice in rules.py, engine.py, and earning tests
Task B: T025-T034 - US2 redemption and approval slice in redemption/approval tests and engine.py
Task C: T035-T041 - US3 tier rules, tier tests, and Tier-Recalculation Agent instructions
Task D: T042-T046 - US4 safe lookup, privacy tests, and adapter projection
```

## Implementation Strategy

### MVP First (US1 Only)

1. Complete Phase 1 setup and Phase 2 foundation.
2. Complete US1 earning, promotions, balance mutation, audit, and AC-1/AC-2 tests.
3. Run the US1 checkpoint and demonstrate deterministic earning locally.
4. Continue immediately to US2 and US3 because redemption approval and tier integrity are mandatory
   project requirements, even though US1 is the smallest demonstrable slice.

### Mandatory Incremental Delivery

1. Foundation: models, JSON dataset, store, audit, errors.
2. US1: earning and promotions with AC-1/AC-2.
3. US2: redemption and human approval with AC-3/AC-4/AC-6.
4. US3: tier recalculation and custom agent with AC-5.
5. US4: PII-safe lookup and external-output boundaries.
6. US5: local demonstration and README.
7. Run all six acceptance tests and cross-cutting privacy/state/determinism tests.
8. Attempt optional MCP only after mandatory completion.

### Two-Hour Capstone Cut Line

If time is constrained, stop after T050. The mandatory deliverable is complete when the core engine,
all six acceptance tests, audit/state invariants, tier agent contract, privacy boundaries, local demo,
and README are complete. T051-T054 are optional and may be omitted without reducing mandatory
acceptance coverage.

## Completion Criteria

- All tasks for the selected scope are checked off with implementation and test files present.
- AC-1 through AC-6 have explicit passing pytest coverage.
- Failed, rejected, and pending operations leave points balance unchanged.
- Every successful points mutation has a safe audit/transaction record.
- Repeated calculations are deterministic; promotion and tier boundaries are tested.
- Tier-Recalculation Agent delegates to the engine and cannot mutate points or invent rules.
- External responses exclude member email and unnecessary PII.
- Local demo and README work from Windows VS Code without cloud/database/web/auth services.
- Optional MCP is either safely implemented or explicitly documented as omitted.
