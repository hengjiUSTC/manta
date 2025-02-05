import unittest
from typing import Any, Dict, Set
from unittest.mock import Mock, patch

from code_manta.tools.manager import (
    ParsedTool,
    Tool,
    ToolManager,
    ToolParser,
    ToolResult,
)


class MockTool(Tool):
    def __init__(self, name: str, description: str):
        self._name = name
        self._description = description

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def validate_params(self, params: Dict[str, Any]) -> None:
        pass

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        return ToolResult(success=True, message="Mock execution")


class TestToolParser(unittest.TestCase):
    def setUp(self):
        self.allowed_tools = {
            "attempt_completion",
            "ask_followup_question",
            "replace_in_file",
            "write_to_file",
            "read_file",
            "execute_command",
        }
        self.parser = ToolParser(self.allowed_tools)

    def test_parse_attempt_completion(self):
        response = """Some text before
<attempt_completion>
<result>Test result</result>
<command>test command</command>
</attempt_completion>
Some text after"""

        parsed = self.parser.parse(response)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.name, "attempt_completion")
        self.assertEqual(parsed.params["result"], "Test result")
        self.assertEqual(parsed.params["command"], "test command")

    def test_parse_ask_followup_question(self):
        response = "<ask_followup_question><question>Test question?</question></ask_followup_question>"
        parsed = self.parser.parse(response)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.name, "ask_followup_question")
        self.assertEqual(parsed.params["question"], "Test question?")

    def test_parse_replace_in_file(self):
        response = """
<replace_in_file>
<path>/test/path.txt</path>
<diff>
<<<<<<< SEARCH
old content
=======
new content
>>>>>>> REPLACE
</diff>
</replace_in_file>
"""
        parsed = self.parser.parse(response)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.name, "replace_in_file")
        self.assertEqual(parsed.params["path"], "/test/path.txt")
        self.assertTrue("diff" in parsed.params)

    def test_parse_write_to_file(self):
        response = """
<write_to_file>
<path>/test/path.txt</path>
<content>
Test content
Multiple lines
</content>
</write_to_file>
"""
        parsed = self.parser.parse(response)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.name, "write_to_file")
        self.assertEqual(parsed.params["path"], "/test/path.txt")
        self.assertTrue("content" in parsed.params)

    def test_parse_read_file(self):
        response = "<read_file><path>/test/path.txt</path></read_file>"
        parsed = self.parser.parse(response)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.name, "read_file")
        self.assertEqual(parsed.params["path"], "/test/path.txt")

    def test_parse_execute_command(self):
        response = """
<execute_command>
<command>ls -la</command>
<requires_approval>true</requires_approval>
</execute_command>
"""
        parsed = self.parser.parse(response)
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed.name, "execute_command")
        self.assertEqual(parsed.params["command"], "ls -la")
        self.assertEqual(parsed.params["requires_approval"], "true")

    def test_parse_invalid_tool(self):
        response = "<invalid_tool><param>value</param></invalid_tool>"
        parsed = self.parser.parse(response)
        self.assertIsNone(parsed)

    def test_parse_malformed_tool(self):
        response = (
            "<attempt_completion><result>Test</result><command>"  # Missing closing tags
        )
        parsed = self.parser.parse(response)
        self.assertIsNone(parsed)


class TestToolManager(unittest.TestCase):
    def setUp(self):
        self.manager = ToolManager()
        self.mock_tools = [
            MockTool("attempt_completion", "Attempt completion tool"),
            MockTool("ask_followup_question", "Ask followup question tool"),
            MockTool("replace_in_file", "Replace in file tool"),
            MockTool("write_to_file", "Write to file tool"),
            MockTool("read_file", "Read file tool"),
            MockTool("execute_command", "Execute command tool"),
        ]
        self.manager.register_tools(self.mock_tools)

    def test_register_tool(self):
        new_tool = MockTool("new_tool", "New tool description")
        self.manager.register_tool(new_tool)
        self.assertIn("new_tool", self.manager.tools)

    def test_register_tools(self):
        for tool in self.mock_tools:
            self.assertIn(tool.name, self.manager.tools)

    def test_get_tools_description(self):
        description = self.manager.get_tools_description()
        for tool in self.mock_tools:
            self.assertIn(tool.description, description)

    def test_parse_tool_use(self):
        response = "<read_file><path>/test/path.txt</path></read_file>"
        tool_name, params = self.manager.parse_tool_use(response)
        self.assertEqual(tool_name, "read_file")
        self.assertEqual(params["path"], "/test/path.txt")

    def test_execute_tool(self):
        result = self.manager.execute_tool("read_file", {"path": "/test/path.txt"})
        self.assertTrue(result.success)

    def test_execute_unknown_tool(self):
        result = self.manager.execute_tool("unknown_tool", {})
        self.assertFalse(result.success)
        self.assertIn("Unknown tool", result.message)

    def test_execute_tool_with_exception(self):
        mock_tool = Mock(spec=Tool)
        mock_tool.name = "failing_tool"
        mock_tool.validate_params.side_effect = ValueError("Invalid params")

        self.manager.register_tool(mock_tool)
        result = self.manager.execute_tool("failing_tool", {})
        self.assertFalse(result.success)
        self.assertIn("Tool execution failed", result.message)


if __name__ == "__main__":
    unittest.main()
