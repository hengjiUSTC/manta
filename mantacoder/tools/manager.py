import re
from dataclasses import dataclass
from typing import Any, Dict, Optional, Set, Tuple, Type

from .base import Tool, ToolResult


@dataclass
class ParsedTool:
    """Parsed tool information."""

    name: str
    params: Dict[str, Any]


class ToolParser:
    """Parser for tool commands in responses."""

    def __init__(self, allowed_tools: Set[str]):
        self.allowed_tools = allowed_tools
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Compile regex patterns for tool parsing."""
        tool_pattern = "|".join(self.allowed_tools)
        self.tool_regex = re.compile(f"<({tool_pattern})>(.*?)</\\1>", re.DOTALL)
        self.param_regex = re.compile(r"<(\w+)>(.*?)</\1>", re.DOTALL)

    def parse(self, response: str) -> Optional[ParsedTool]:
        """Parse a response to extract tool use.

        Args:
            response: Response string to parse

        Returns:
            ParsedTool if tool found, None otherwise
        """
        tool_match = self.tool_regex.search(response)
        if not tool_match:
            return None

        tool_name = tool_match.group(1)
        content = tool_match.group(2)

        # Parse parameters
        params = {}
        param_matches = self.param_regex.findall(content)
        for param, value in param_matches:
            params[param] = value

        return ParsedTool(name=tool_name, params=params)


class ToolManager:
    """Manages tool registration, parsing, and execution."""

    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self.parser: Optional[ToolParser] = None

    def register_tool(self, tool: Tool) -> None:
        """Register a new tool."""
        self.tools[tool.name] = tool
        # Update parser with new tool
        self._update_parser()

    def register_tools(self, tools: list[Tool]) -> None:
        """Register multiple tools at once."""
        for tool in tools:
            self.tools[tool.name] = tool
        # Update parser after all tools are registered
        self._update_parser()

    def _update_parser(self) -> None:
        """Update the tool parser with current set of tools."""
        self.parser = ToolParser(set(self.tools.keys()))

    def get_tools_description(self) -> str:
        """Get formatted description of all registered tools."""
        if not self.tools:
            return "No tools registered."

        descriptions = []
        for _, tool in self.tools.items():
            descriptions.append(tool.description)

        return "\n\n".join(descriptions)

    def parse_tool_use(
        self, response: str
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """Parse tool use from response string.

        Args:
            response: Response string to parse

        Returns:
            Tuple of (tool_name, parameters) if tool found, (None, None) otherwise
        """
        if not self.parser:
            self._update_parser()
        parsed = None
        if self.parser:
            parsed = self.parser.parse(response)
        if parsed:
            return parsed.name, parsed.params
        return None, None

    def execute_tool(self, tool_name: str, params: Dict[str, Any] | None) -> ToolResult:
        """Execute a tool by name with given parameters."""
        tool = self.tools.get(tool_name)
        if not tool:
            return ToolResult(success=False, message=f"Unknown tool: {tool_name}")

        try:
            if params is None:
                params = {}
            tool.validate_params(params)
            return tool.execute(params)
        except Exception as e:
            return ToolResult(success=False, message=f"Tool execution failed: {str(e)}")
