from pathlib import Path


def test_tier_agent_contract_is_delegation_only():
    path = Path(".github/agents/tier-recalculation.agent.md")
    text = path.read_text(encoding="utf-8")
    assert "recalc_tier()" in text
    assert "source of truth" in text
    assert "Never invent thresholds" in text
    assert "points balance" in text
    assert "PII" in text
