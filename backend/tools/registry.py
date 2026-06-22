from typing import Any
from tools.base import BaseTool

_registry: dict[str, BaseTool] = {}

def register(tool: BaseTool) -> None:
    """Register a tool so the agent can discover it."""
    _registry[tool.name] = tool

def get_tool(name: str) -> BaseTool | None:
    """Look up a tool by name."""
    return _registry.get(name)

def list_tools() -> list[BaseTool]:
    """Return all registered tools."""
    return list(_registry.values())

def tool_descriptions() -> str:
    """Format all tool descriptions for inclusion in the system prompt."""
    lines: list[str] = []
    for tool in list_tools():
        lines.append(f"  - {tool.name}: {tool.description}")
        lines.append(f"    Parameters: {tool.parameters}")
    return "\n".join(lines)