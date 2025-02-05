from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class ToolResult:
    """Result of tool execution."""

    success: bool
    message: str
    data: Optional[Any] = None


class Tool(ABC):
    """Base class for all tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Get tool name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Get tool description."""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """Execute the tool with given parameters."""
        pass

    def validate_params(self, params: Dict[str, Any]) -> None:
        """Validate parameters before execution."""
        pass
