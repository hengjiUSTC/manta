import logging
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from code_manta.core.config import Config
from code_manta.llm.client import LLMClient
from code_manta.session.history import ConversationHistory
from code_manta.tools.ask_user import AskUserTool
from code_manta.tools.attempt_completion import AttemptCompletion
from code_manta.tools.command_line import CommandExecutionTool
from code_manta.tools.manager import ToolManager
from code_manta.tools.read_file import ReadFileTool
from code_manta.tools.replace_file import ReplaceFileTool
from code_manta.tools.write_file import WriteFileTool


class ResponseType(Enum):
    TOOL_CALL = "tool_call"
    FINAL_RESPONSE = "final_response"


@dataclass
class ProcessedResponse:
    type: ResponseType
    content: str
    tool_name: Optional[str] = None
    tool_params: Optional[dict] = None


class ReplyHandler:
    def __init__(self, config: Config, conversations: ConversationHistory):
        self.api_handler = LLMClient(config)
        self.conversations = conversations
        self.tool_manager = self._setup_tools()

    def _setup_tools(self) -> ToolManager:
        manager = ToolManager()
        manager.register_tools(
            [
                CommandExecutionTool(),
                ReadFileTool(),
                WriteFileTool(),
                ReplaceFileTool(),
                AskUserTool(),
                AttemptCompletion(),
            ]
        )
        return manager

    def _ask_permission(self, tool: str) -> bool:
        while True:
            response = (
                input(f"Do you want to execute the tool '{tool}'? (yes/no): ")
                .strip()
                .lower()
            )
            if response in ["yes", "no"]:
                return response == "yes"
            print("Please answer 'yes' or 'no'.")

    def get_tools_description(self):
        return self.tool_manager.get_tools_description()

    def process_response(self, response: str) -> ProcessedResponse:
        """Process an LLM response and determine if it's a tool call or final response."""
        self.conversations.add_message("assistant", response)
        tool, params = self.tool_manager.parse_tool_use(response)

        if tool:
            return ProcessedResponse(
                type=ResponseType.TOOL_CALL,
                content=response,
                tool_name=tool,
                tool_params=params,
            )
        return ProcessedResponse(type=ResponseType.FINAL_RESPONSE, content=response)

    def execute_tool(self, tool: str, params: dict) -> Optional[str]:
        """Execute a tool and return the result."""
        result = self.tool_manager.execute_tool(tool, params)

        # Add tool execution results to conversation
        if result.message:
            self.conversations.add_message("user", str(result.message))
        if result.data:
            self.conversations.add_message("user", str(result.data))

        return result.message

    def get_next_response(self) -> str:
        """Get next response from LLM based on current conversation context."""
        return self.api_handler.chat(self.conversations.get_context())

    def handle_tool_denial(self, tool: str | None):
        """Handle when user denies tool execution."""
        denial_message = f"Tool execution denied: {tool}"
        self.conversations.add_message("user", denial_message)
        logging.debug(f"Tool '{tool}' execution was denied by the user.")
