import logging
import os
import subprocess
from typing import Any, Dict, Optional

from manta.tools.base import Tool, ToolResult


class CommandExecutionTool(Tool):
    """Tool for executing command line commands with automatic working directory
    detection.
    """

    def __init__(self):
        """Initialize the command execution tool."""
        # Move up to the project root directory
        self.working_dir = os.getcwd()
        logging.debug(f"!!!!!!!!Working directory: {self.working_dir}")

    @property
    def name(self) -> str:
        return "execute_command"

    @property
    def description(self) -> str:
        return f"""
## execute_command
Description: Request to execute a CLI command on the system. Use this when you need to perform system operations or run specific commands to accomplish any step in the user's task. You must tailor your command to the user's system and provide a clear explanation of what the command does. Prefer to execute complex CLI commands over creating executable scripts, as they are more flexible and easier to run. Commands will be executed in the current working directory: {self.working_dir}

Parameters:
- command: (required) The CLI command to execute. This should be valid for the current operating system. Ensure the command is properly formatted and does not contain any harmful instructions.

Usage: <execute_command> <command>Your command here</command> </execute_command>
"""

    def _resolve_working_dir(self, specified_dir: Optional[str] = None) -> str:
        """Resolve the working directory path.

        Args:
            specified_dir: Optional directory path to use instead of default

        Returns:
            Absolute path to the working directory
        """
        if not specified_dir:
            return self.working_dir

        # If relative path, make it relative to the default working directory
        if not os.path.isabs(specified_dir):
            resolved_path = os.path.join(self.working_dir, specified_dir)
        else:
            resolved_path = specified_dir

        # Normalize the path
        resolved_path = os.path.abspath(resolved_path)

        # Validate the directory exists
        if not os.path.exists(resolved_path):
            raise ValueError(f"Directory does not exist: {resolved_path}")

        return resolved_path

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            # Extract parameters
            command = params["command"]
            timeout = int(params.get("timeout", 30))

            # logging.debug execution info
            print(f"Executing command: {command}")
            logging.debug(f"Working directory: {self.working_dir}")
            logging.debug(f"Timeout: {timeout} seconds")

            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.working_dir,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                )

                # Prepare output with command execution details
                output = [
                    f"Command: {command}",
                    f"Working Directory: {self.working_dir}",
                    f"Exit Code: {result.returncode}",
                ]

                if result.stdout:
                    output.append("STDOUT:")
                    output.append(result.stdout.rstrip())
                if result.stderr:
                    output.append("STDERR:")
                    output.append(result.stderr.rstrip())

                # Return based on execution result
                if result.returncode == 0:
                    return ToolResult(
                        success=True,
                        message="Command executed successfully",
                        data="\n".join(output),
                    )
                else:
                    return ToolResult(
                        success=False,
                        message=f"Command failed with exit code {result.returncode}",
                        data="\n".join(output),
                    )

            except subprocess.TimeoutExpired:
                return ToolResult(
                    success=False,
                    message=f"Command timed out after {timeout} seconds",
                    data=f"Command: {command}\nWorking Directory: {self.working_dir}",
                )

            except subprocess.SubprocessError as e:
                return ToolResult(
                    success=False,
                    message=f"Failed to execute command: {str(e)}",
                    data=f"Command: {command}\nWorking Directory: {self.working_dir}",
                )

        except Exception as e:
            return ToolResult(
                success=False, message=f"Error executing command: {str(e)}"
            )


# Example usage and test
def test_command_tool():
    # Create tool instance
    cmd_tool = CommandExecutionTool()

    # Test cases
    test_cases = [
        # Test with default working directory
        {"command": "pwd", "expected_success": True},
        # Test with relative path
        {"command": "ls -la", "working_dir": ".", "expected_success": True},
        # Test command with output
        {"command": "echo 'Testing command output'", "expected_success": True},
        # Test invalid working directory
        {
            "command": "ls",
            "working_dir": "/nonexistent/directory",
            "expected_success": False,
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        logging.debug(f"\nRunning test case {i}:")
        result = cmd_tool.execute(test_case)
        logging.debug(f"Success: {result.success}")
        logging.debug(f"Message: {result.message}")
        if result.data:
            logging.debug(f"Data:\n{result.data}")
        error_msg = (
            f"Test case {i} failed: "
            f"expected success={test_case['expected_success']}, "
            f"got {result.success}"
        )
        assert result.success == test_case["expected_success"], error_msg
        logging.debug(f"Test case {i} passed")


if __name__ == "__main__":
    test_command_tool()
