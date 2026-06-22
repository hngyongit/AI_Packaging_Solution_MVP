"""
Template for a search_contract tool.

Replace this file with your own implementation, or delete it if you don't
need a contract-search tool. See tools/base.py for the BaseTool interface.
"""
from tools.base import BaseTool


class SearchContract(BaseTool):
    """Search contracts by keyword."""

    @property
    def name(self) -> str:
        return "search_contract"

    @property
    def description(self) -> str:
        return "Search for contracts by keyword."

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword or phrase to search for",
                }
            },
            "required": ["query"],
        }

    async def run(self, query: str) -> str:
        # TODO: Replace with real implementation
        raise NotImplementedError("search_contract is not yet implemented")