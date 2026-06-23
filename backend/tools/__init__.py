from tools.base import BaseTool
from tools.registry import get_tool, list_tools, tool_descriptions
from tools.generate_mockup import GenerateMockup
from tools.registry import register

# ── Auto-register all tools ────────────────────────────────────
register(GenerateMockup())

__all__ = [
    "BaseTool",
    "get_tool",
    "list_tools",
    "tool_descriptions",
]
