# Implementation Plan: Loyalty & Rewards Engine

**Branch**: `001-loyalty-rewards-engine` | **Date**: 2026-09-04 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-loyalty-rewards-engine/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

Build a lightweight, deterministic loyalty rules engine whose pure business functions calculate
earning, promotions, redemption, approval gates, and tier changes. Pydantic v2 models validate
domain data, a local JSON store supplies demonstration data, and pytest verifies AC-1 through AC-6
plus state, audit, determinism, boundary, and privacy behavior. Agents and the optional MCP lookup
delegate to the engine and expose only safe explanations or member fields.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11+

**Primary Dependencies**: Pydantic v2; pytest; Python `Decimal` arithmetic from the standard
library; no web framework or agent runtime required

**Storage**: Local JSON dataset and in-memory operation state for the demonstration

**Testing**: pytest with unit tests for pure rules, focused integration tests for workflows, static
agent-instruction contract tests, and a mocked agent-delegation test; no LLM or Copilot runtime
required

**Target Platform**: Windows local development from VS Code; offline-capable

**Project Type**: Python library with a local demonstration entry point and optional tool/agent adapters

**Performance Goals**: Complete the documented local demonstration in under 10 minutes; no
  production throughput target for the capstone

**Constraints**: No database, cloud infrastructure, web frontend, authentication service, or
  unnecessary enterprise infrastructure. Core calculations must be deterministic and independent
  of LLM judgment. Monetary and multiplier calculations MUST use Decimal arithmetic, and final
  points MUST be rounded once with ROUND_HALF_UP. MCP is optional and must not be a core dependency.

**Scale/Scope**: Small local dataset and one demonstrable member workflow; suitable for a two-hour
  capstone implementation. Scope includes earning, promotions, redemption, approvals, tiers, audit,
  tests, a custom Tier-Recalculation Agent, and optional MCP lookup.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The following gates pass before research and must pass again after design:

- **Deterministic rules**: Core earning, promotion, redemption, approval, and tier decisions are
  pure/testable functions; agents and adapters delegate rather than decide.
- **Auditability and balance safety**: Every committed balance mutation creates a transaction or
  audit event; rejected and pending operations do not mutate balances.
- **Human approval**: `human_gate_redeem_over` is read from rules configuration, with 30000 points
  in the project dataset; high-value points are deducted only after explicit approval.
- **Promotion and tier integrity**: Eligibility, stackability, and tier thresholds are configured
  and deterministic; non-stackable promotions are applied at most once per earning event.
- **Privacy**: External responses, agent output, optional MCP output, logs, and demonstrations omit
  email and unnecessary PII.
- **Testability and traceability**: AC-1 through AC-6 have pytest coverage, and requirements map to
  plan artifacts and later tasks.
- **Scope**: The design uses local JSON and in-memory state; no unjustified infrastructure is added.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
src/
└── loyalty_rewards/
  ├── models.py              # Pydantic domain and result models
  ├── rules.py               # Pure earning, promotion, redemption, and tier rules
  ├── store.py               # Local JSON loading and in-memory state access
  ├── audit.py               # Transaction/event creation and safe audit views
  ├── engine.py              # Explicit orchestration and state mutation boundaries
  ├── adapters.py            # Safe member lookup and optional MCP-facing adapter
  └── demo.py                # Local end-to-end demonstration

data/
└── members.json               # Sample members, tiers, rewards, promotions, and rules

.github/
└── agents/
  └── tier-recalculation.agent.md  # Custom agent instructions; delegates to engine

tests/
├── unit/                      # Pure rules, models, promotion, tier, and privacy tests
└── integration/               # Full earn, redeem, approval, audit, store, and demo flows
```

**Structure Decision**: Select one small Python package under `src/loyalty_rewards` with explicit
domain, rules, store, audit, orchestration, and adapter boundaries. Keep pure calculations in
`rules.py`, keep mutations in `engine.py`, and keep external presentation concerns in adapters.
Use `data/members.json` only as local source data. The custom agent is configuration/instructions,
not a second rules implementation. Validate it with static text checks against
`.github/agents/tier-recalculation.agent.md` and a mocked delegation test that spies on
`engine.recalc_tier()`; do not add an LLM runtime. The MCP adapter is optional and must be
removable without changing core engine behavior.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | The design uses one lightweight local project and no unnecessary infrastructure. |
