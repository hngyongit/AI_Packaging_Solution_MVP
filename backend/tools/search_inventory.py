"""
Template for a search_inventory tool.

Replace this file with your own implementation, or delete it if you don't
need an inventory-search tool. See tools/base.py for the BaseTool interface.
"""
from tools.base import BaseTool


class SearchInventory(BaseTool):
    """Search inventory items."""

    @property
    def name(self) -> str:
        return "search_inventory"

    @property
    def description(self) -> str:
        return "Search current inventory by item name or category."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "item_name": {
                    "type": "string",
                    "description": "Item name or category to look up",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum results (default 5)",
                    "default": 5,
                },
            },
            "required": ["item_name"],
        }

    async def run(self, item_name: str, max_results: int = 5) -> str:
        # TODO: Replace with real implementation
        raise NotImplementedError("search_inventory is not yet implemented")