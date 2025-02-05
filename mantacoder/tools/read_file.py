import logging
import os
from typing import Any, Dict

from mantacoder.tools.base import Tool, ToolResult
from mantacoder.tools.file_utils import FileUtils


class ReadFileTool(Tool):
    def __init__(self):
        """Initialize the command execution tool."""
        # Move up to the project root directory
        self.working_dir = os.getcwd()
        logging.debug(f"!!!!!!!!Working ReadFileTool directory: {self.working_dir}")

    @property
    def name(self) -> str:
        return "read_file"

    @property
    def description(self) -> str:
        return f"""
## read_file
Description: Request to read the contents of a file at the specified path. Use this when you need to examine the contents of an existing file you do not know the contents of, for example to analyze code, review text files, or extract information from configuration files. Automatically extracts raw text from PDF and DOCX files. May not be suitable for other types of binary files, as it returns the raw content as a string.

Parameters:
- path: (required) The path of the file to read (relative to the current working directory {self.working_dir})

Usage: <read_file> <path>File path here</path> </read_file>
"""

    def validate_params(self, params: Dict[str, Any]) -> None:
        if "path" not in params:
            raise ValueError("Missing required parameter 'path'")

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            self.validate_params(params)
            content = FileUtils.read_file(params["path"])
            return ToolResult(
                success=True,
                message=f"Successfully read file: {params['path']}",
                data=content,
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to read file: {str(e)}")
