from subprocess import CalledProcessError, run
from typing import Any, Dict

from code_manta.tools.base import Tool, ToolResult


class AttemptCompletion(Tool):
    @property
    def name(self) -> str:
        return "attempt_completion"

    @property
    def description(self) -> str:
        return """
## attempt_completion
Description: After each tool use, the user will respond with the result of that tool use, i.e. if it succeeded or failed, along with any reasons for failure. Once you've received the results of tool uses and can confirm that the task is complete, use this tool to present the result of your work to the user. Optionally you may provide a CLI command to showcase the result of your work. The user may respond with feedback if they are not satisfied with the result, which you can use to make improvements and try again.
IMPORTANT NOTE: This tool CANNOT be used until you've confirmed from the user that any previous tool uses were successful. Failure to do so will result in code corruption and system failure. Before using this tool, you must ask yourself in <thinking></thinking> tags if you've confirmed from the user that any previous tool uses were successful. If not, then DO NOT use this tool.
Parameters:
- result: (required) The result of the task. Formulate this result in a way that is final and does not require further input from the user. Don't end your result with questions or offers for further assistance.
- command: (optional) A CLI command to execute to show a live demo of the result to the user. For example, use `open index.html` to display a created html website, or `open localhost:3000` to display a locally running development server. But DO NOT use commands like `echo` or `cat` that merely print text. This command should be valid for the current operating system. Ensure the command is properly formatted and does not contain any harmful instructions.
Usage:
<attempt_completion>
<result>
Your final result description here
</result>
<command>Command to demonstrate result (optional)</command>
</attempt_completion>
"""

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        result = params.get("result")
        command = params.get("command")

        # Print the result of the task to the user
        print(f"Task completion result: {result}")

        # If a command is provided, attempt to execute it
        if command:
            try:
                # Print the command description for the user
                print(f"Executing command: {command}")

                # Run the command using subprocess
                run(command, shell=True, check=True)

                # If successful, return success message
                return ToolResult(
                    success=True,
                    message="Completion result displayed and command executed successfully.",
                )
            except CalledProcessError as e:
                # Handle cases where the command fails
                error_message = f"Failed to execute command: {command}. Error: {str(e)}"
                print(error_message)
                return ToolResult(success=False, message=error_message)

        # Return the result information as a success
        return ToolResult(success=True, message="Completion result displayed.")
