# Quickstart: Local Validation

## Prerequisites

- Windows with VS Code.
- Python 3.11 or newer available as `python`.
- Repository opened at the project root.

## Setup

Create and activate a local virtual environment, then install the project and test dependencies
according to the implementation task's chosen packaging setup. The implementation must include
Pydantic v2 and pytest; no cloud credentials, database, web server, or authentication service is
required.

Example PowerShell setup:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

## Run Automated Validation

```powershell
python -m pytest
```

The suite must include explicit tests for:

- AC-1: GOLD earning of 100 USD produces 1250 base points before promotions.
- AC-2: ROOM EARN_MULTIPLIER promotion applies once and respects non-stackability.
- AC-3: 42500 minus 15000 commits to 27500 and records `REDEEM`.
- AC-4: insufficient balance rejects without mutation.
- AC-5: lifetime threshold crossing upgrades tier deterministically.
- AC-6: redemption over configured 30000 threshold requires approval before commit.

It must also cover rejected/pending state preservation, approved high-value redemption, audit
records, threshold boundaries, repeated deterministic calculations, and PII exclusion.

## Run the Demonstration

The implementation should provide a simple local entry point, for example:

```powershell
python -m loyalty_rewards.demo
```

The demonstration should visibly show, in order:

1. A member lookup with safe fields only.
2. Earning from an eligible room or flight activity.
3. Promotion evaluation and exactly-once application.
4. A successful award-night redemption and audit record.
5. An insufficient-balance rejection with unchanged balance.
6. A suite redemption entering pending approval with unchanged balance.
7. Explicit approval committing the suite redemption and recording audit evidence.
8. Tier recalculation at a threshold boundary.
9. The Tier-Recalculation Agent explanation, using the same deterministic result.
10. The audit trail without member email or unnecessary PII.

If MCP is implemented, demonstrate the safe `lookup_member` projection separately. If it is
omitted due to the capstone time limit, the core demonstration and all mandatory tests still pass.

## Validation References

- Domain fields and state transitions: [data-model.md](data-model.md)
- Engine behavior: [contracts/engine-contract.md](contracts/engine-contract.md)
- Adapter boundaries: [contracts/external-adapters.md](contracts/external-adapters.md)
- Acceptance requirements: [spec.md](spec.md)
