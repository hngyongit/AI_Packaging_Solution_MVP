from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base class for all AI-callable tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name — the LLM uses this to reference the tool."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Natural-language description so the LLM knows when to call it."""
        ...

    @property
    @abstractmethod
    def parameters(self) -> dict:
        """JSON-schema describing the parameters the tool accepts."""
        ...

    @abstractmethod
    async def run(self, **kwargs) -> str:
        """Execute the tool. Returns a string result to inject back into the LLM."""
        ...
