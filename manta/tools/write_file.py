import os
from typing import Any, Dict

from manta.tools.base import Tool, ToolResult

from .file_utils import FileUtils


class WriteFileTool(Tool):
    @property
    def name(self) -> str:
        return "write_to_file"

    @property
    def description(self) -> str:
        return f"""
## write_to_file
Description: Request to write content to a file at the specified path. If the file exists, it will be overwritten with the provided content. If the file doesn't exist, it will be created. This tool will automatically create any directories needed to write the file.
Parameters:
- path: (required) The path of the file to write to (relative to the current working directory ${os.getcwd()})
- content: (required) The content to write to the file. ALWAYS provide the COMPLETE intended content of the file, without any truncation or omissions. You MUST include ALL parts of the file, even if they haven't been modified.
Usage:
<write_to_file>
<path>File path here</path>
<content>
Your file content here
</content>
</write_to_file>
"""

    def validate_params(self, params: Dict[str, Any]) -> None:
        if "path" not in params:
            raise ValueError("Missing required parameter 'path'")
        if "content" not in params:
            raise ValueError("Missing required parameter 'content'")

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            self.validate_params(params)
            FileUtils.write_file(params["path"], params["content"])
            return ToolResult(
                success=True, message=f"Successfully wrote to file: {params['path']}"
            )
        except Exception as e:
            return ToolResult(success=False, message=f"Failed to write file: {str(e)}")
