<!--
Sync Impact Report
Version change: Unratified scaffold -> 1.0.0
Modified principles: None; this is the initial project constitution.
Added sections: Ten Core Principles; Scope and Definitions; Development Workflow.
Removed sections: None.
Follow-up TODOs: None.
-->

# Loyalty & Rewards Engine Constitution

## Core Principles

### I. Deterministic Business Rules
Identical inputs, member state, and rule configuration MUST always produce the same
result. Business-critical calculations MUST NOT depend on LLM judgment or other
non-deterministic agent behavior. This makes outcomes reproducible and reviewable.

### II. Auditability
Every points balance mutation MUST produce an auditable transaction or event. Earn and
redemption operations MUST record what changed, why it changed, and which member was
affected. Audit records are part of the operation contract, not an optional diagnostic.

### III. No Silent Balance Changes
A member's points balance MUST change only through an explicit rules-engine operation.
Failed or rejected operations MUST leave the balance unchanged and MUST expose the
failure outcome to the caller. This prevents untraceable state changes.

### IV. Human Governance for High-Value Redemption
Redemptions above the configured `human_gate_redeem_over` threshold MUST receive
explicit human approval before points are deducted or the redemption is committed. The
threshold MUST come from configured rules and MUST NOT be duplicated as a magic number.

### V. Separation of Deterministic Logic and Agents
The core rules engine is the source of truth for earning, promotions, redemption, and
tier calculation. Agents MAY orchestrate workflows, retrieve information, and explain
results, but MUST NOT invent, override, or independently apply business rules.

### VI. Promotion Safety
Promotions MUST be applied according to explicit eligibility and stackability rules. A
non-stackable promotion MUST NOT be applied more than once to the same earning event.
Promotion evaluation MUST make the eligibility and application decision testable.

### VII. Tier Calculation Integrity
Tier recalculation MUST be deterministic and based on defined tier thresholds and
lifetime points. Tier-recalculation agents MUST invoke the deterministic rules engine
and MUST NOT independently decide a member's tier.

### VIII. Security and Privacy
Member emails and other personally identifiable information MUST NOT be exposed through
agent responses, MCP tools, logs, or demonstrations unless explicitly required for the
operation. Interfaces MUST return only the minimum member information needed.

### IX. Testability
Core business rules MUST be implemented as pure, testable functions wherever practical.
All six acceptance criteria from the project brief MUST have automated pytest coverage.
Tests MUST cover rejected operations, audit records, approval gates, promotion safety,
and deterministic tier outcomes where those behaviors apply.

### X. Traceability
Requirements, implementation tasks, tests, and acceptance criteria MUST remain
traceable through the Spec Kit artifacts. Changes that cannot be traced to a requirement
or acceptance criterion MUST be justified in the relevant planning artifact.

## Scope and Definitions

This constitution governs the Loyalty & Rewards Engine, including its deterministic
rules engine, agent integrations, MCP interfaces, member balance operations,
promotions, redemptions, and tier calculations. "Rules configuration" means the
versioned configuration used by the rules engine, including approval thresholds,
eligibility rules, stackability rules, and tier thresholds.

## Development Workflow

Every change affecting points, promotions, redemptions, or tiers MUST include or update
automated tests and the applicable Spec Kit requirement, plan, or task trace. Reviews
MUST verify deterministic behavior, audit coverage, balance invariants, privacy
minimization, and the relevant acceptance criteria before the change is accepted.

## Governance

This constitution governs engineering decisions for the Loyalty & Rewards Engine.
Amendments MUST be proposed as a documented change to this file, identify affected
principles and artifacts, and receive project-owner approval before implementation.
Constitution amendments MUST preserve the ten-principle structure unless an amendment
explicitly documents a change in scope.

The version follows semantic versioning. A MAJOR increment is required for removing or
redefining a principle or making governance backward-incompatible. A MINOR increment
is required for adding a principle or materially expanding governance. A PATCH increment
is required for clarifications, wording fixes, or other non-semantic refinements.

Every feature review MUST check compliance with this constitution. Non-compliance MUST
be corrected before acceptance or explicitly documented with project-owner approval.
The constitution MUST be reviewed whenever acceptance criteria, rules configuration
contracts, or agent responsibilities materially change.

**Version**: 1.0.0 | **Ratified**: 2026-09-04 | **Last Amended**: 2026-09-04
