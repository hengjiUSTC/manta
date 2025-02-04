import os
from typing import Any, Dict

from manta.tools.base import Tool, ToolResult


class AskUserTool(Tool):
    @property
    def name(self) -> str:
        return "ask_followup_question"

    @property
    def description(self) -> str:
        return """
## ask_followup_question
Description: Ask the user a question to gather additional information needed to complete the task. This tool should be used when you encounter ambiguities, need clarification, or require more details to proceed effectively. It allows for interactive problem-solving by enabling direct communication with the user. Use this tool judiciously to maintain a balance between gathering necessary information and avoiding excessive back-and-forth.
Parameters:
- question: (required) The question to ask the user. This should be a clear, specific question that addresses the information you need.
Usage:
<ask_followup_question>
<question>Your question here</question>
</ask_followup_question>
"""

    def validate_params(self, params: Dict[str, Any]) -> None:
        if "question" not in params:
            raise ValueError("Missing required parameter 'question'")

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            self.validate_params(params)
            question = params.get("question")

            # Print the question to the user
            print(question)

            # Collect the user's response
            user_response = input("User's response: ")

            # Return the response as a ToolResult
            return ToolResult(
                success=True,
                message="User's response displayed.",
                data={"response": user_response},
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to ask user: {str(e)}")
