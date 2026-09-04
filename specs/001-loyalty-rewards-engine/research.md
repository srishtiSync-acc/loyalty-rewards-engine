# Research: Loyalty & Rewards Engine

## Decision 1: Use a pure-function rules core with a thin stateful orchestrator

**Decision**: Keep points calculations, promotion selection, redemption eligibility,
approval gating, and tier calculation as deterministic functions. Place balance mutation and
transaction persistence behind explicit engine operations.

**Rationale**: The constitution makes the rules engine the source of truth and requires
repeatable, independently testable business calculations. Separating calculations from mutation
also makes failed and pending operations easy to prove state-preserving.

**Alternatives considered**: A single service class was rejected because it would mix policy,
state changes, and audit behavior. LLM-mediated decisions were rejected because business-critical
outcomes cannot depend on agent judgment.

## Decision 2: Use Pydantic v2 for validated domain boundaries

**Decision**: Model members, tiers, activities, promotions, rewards, rules configuration,
transactions, audit events, redemption requests, and safe lookup responses with Pydantic v2.

**Rationale**: The project explicitly requires Pydantic v2. Validation at input and dataset
boundaries prevents malformed money, points, enum, and threshold values from reaching pure rules.

**Alternatives considered**: Unvalidated dictionaries were rejected because they weaken contracts
and make invalid state easier to introduce. A heavier ORM was rejected as unnecessary for local JSON.

## Decision 3: Use local JSON as source data and in-memory state for the capstone

**Decision**: Load a small versioned dataset from `data/members.json`; copy validated records into
an in-memory store for the running demonstration. Keep writes scoped to the process unless the
implementation needs a simple demonstration output file.

**Rationale**: This satisfies local Windows/VS Code execution and the two-hour limit without a
database, cloud dependency, or authentication service.

**Alternatives considered**: A relational database and hosted service were rejected as out of
scope. Purely hardcoded fixtures were rejected because the specification requires a local JSON
data source.

## Decision 4: Treat high-value redemption as an explicit state machine

**Decision**: A redemption at or below `human_gate_redeem_over` can commit after balance
validation. A redemption above the configured threshold enters `PENDING_APPROVAL`, and only an
explicit approval transitions it to `COMMITTED`; rejection transitions it to `REJECTED` without
a balance mutation.

**Rationale**: Explicit states make the no-deduction-before-approval invariant and duplicate
approval/commit behavior testable.

**Alternatives considered**: Deducting points at request time and refunding on rejection was
rejected because it violates the constitution's approval and no-silent-change guarantees.

## Decision 5: Make promotion evaluation event-scoped and deterministic

**Decision**: Evaluate promotions against an immutable earning event and member context. Apply
eligible promotions in a stable configured order, tracking applied promotion IDs within the event.
A non-stackable promotion can contribute at most once to that event.

**Rationale**: Event-scoped application directly enforces the promotion safety principle and
makes repeated evaluation reproducible.

**Alternatives considered**: Applying promotions by arbitrary collection order was rejected because
it can produce inconsistent results. Allowing each caller to decide stackability was rejected
because policy must remain in configuration and the core engine.

## Decision 6: Keep MCP and agent integrations as thin, optional adapters

**Decision**: Implement the Tier-Recalculation Agent as a custom instruction file that invokes
the deterministic tier operation and explains its returned result. Design MCP member lookup as an
optional adapter that reads the store and returns a safe projection without business-rule logic.

**Rationale**: Agents may orchestrate and explain but cannot override rules. MCP is explicitly
optional and must not threaten the mandatory core scope.

**Alternatives considered**: Duplicating tier or points logic in the agent/MCP layer was rejected
because it creates conflicting sources of truth. Making MCP a core dependency was rejected because
all mandatory workflows must remain functional if it is omitted.

## Decision 7: Use pytest layers mapped to acceptance criteria and invariants

**Decision**: Use unit tests for pure rules and integration tests for store-backed engine flows.
Name or group tests by AC-1 through AC-6, and add focused cases for state preservation, audit,
threshold boundaries, deterministic repetition, and PII exclusion.

**Rationale**: The constitution requires automated pytest coverage for all six acceptance criteria,
while the feature risk is concentrated in balance mutation and external data minimization.

**Alternatives considered**: A single end-to-end test was rejected because it would not isolate
calculation failures from state and audit failures.
