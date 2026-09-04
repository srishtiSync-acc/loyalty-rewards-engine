# Loyalty & Rewards Engine

A deterministic, auditable Python loyalty engine for local Windows development in VS Code.
Business rules live in pure functions; the engine owns state mutation and audit events. Agent
instructions orchestrate the engine and never invent rules.

## Windows setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m pytest
python -m loyalty_rewards.demo
```

The local demo covers safe lookup, earning and promotions, redemption, approval, tier recalculation,
and safe audit output. MCP is an optional adapter around the same privacy-safe lookup function.

## Optional MCP server

Install the optional SDK and start the stdio server:

```powershell
python -m pip install -e ".[mcp]"
python -m loyalty_rewards.mcp_server
```

The server exposes `member_lookup`, returning `member_id`, `display_name`, `tier_code`,
`points_balance`, and `lifetime_points`. Unknown members return a controlled error. Email and
other unnecessary PII are never included. The MCP server does not implement loyalty rules.

## Architecture

- `models.py`: validated domain and result types
- `rules.py`: pure Decimal calculations and decisions
- `store.py`: JSON loading and in-memory copies
- `audit.py`: safe immutable audit records
- `engine.py`: explicit mutation boundaries and approval state machine
- `adapters.py`: privacy-safe member projection
- `.github/agents/tier-recalculation.agent.md`: orchestration contract only
