import pytest

pytest.importorskip("mcp")

from loyalty_rewards.mcp_server import create_server


def test_mcp_lookup_returns_safe_known_member(store, member):
    server = create_server(store=store)
    tool = server._tool_manager.get_tool("member_lookup")
    result = tool.fn(member.member_id)

    assert result["member_id"] == member.member_id
    assert result["tier_code"] == "GOLD"
    assert "email" not in result


def test_mcp_lookup_returns_controlled_unknown_member(store):
    server = create_server(store=store)
    tool = server._tool_manager.get_tool("member_lookup")

    assert tool.fn("missing") == {"member_id": "missing", "error": "member not found"}