"""Optional MCP server exposing the privacy-safe member lookup adapter."""

from pathlib import Path
from typing import Any

from .adapters import lookup_member
from .store import InMemoryStore, load_dataset

try:
    from mcp.server.mcpserver import MCPServer
except ImportError as exc:  # pragma: no cover - exercised only without the optional extra
    MCPServer = None
    _MCP_IMPORT_ERROR = exc
else:
    _MCP_IMPORT_ERROR = None


def create_server(store: InMemoryStore | None = None, data_path: str | Path | None = None):
    """Create the optional MCP server around the existing safe lookup adapter."""
    if MCPServer is None:
        raise RuntimeError(
            "MCP support is unavailable; install the optional dependency with "
            "python -m pip install -e \".[mcp]\""
        ) from _MCP_IMPORT_ERROR

    if store is None:
        dataset_path = Path(data_path) if data_path else Path(__file__).parents[2] / "data" / "members.json"
        dataset = load_dataset(dataset_path)
        store = InMemoryStore(dataset.members, dataset.rules)

    server = MCPServer("loyalty-rewards-engine")

    @server.tool(name="member_lookup", description="Look up non-sensitive member fields.")
    def member_lookup(member_id: str) -> dict[str, Any]:
        view = lookup_member(store, member_id)
        if view is None:
            return {"member_id": member_id, "error": "member not found"}
        return view.model_dump(mode="json")

    return server


def main() -> None:
    create_server().run()


if __name__ == "__main__":
    main()
