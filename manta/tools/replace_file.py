import io
import os
from dataclasses import dataclass
from typing import Any, Dict, List

from unidiff import PatchSet

from .base import Tool, ToolResult
from .file_utils import FileUtils


class ReplaceFileTool(Tool):
    @property
    def name(self) -> str:
        return "replace_in_file"

    @property
    def description(self) -> str:
        return """
## replace_in_file
Description: Request to replace sections of content in an existing file using SEARCH/REPLACE blocks that define exact changes to specific parts of the file.
Parameters:
- path: (required) The path of the file to modify
- diff: (required) One or more SEARCH/REPLACE blocks following this format:
```
<<<<<<< SEARCH
[exact content to find]
=======
[new content to replace with]
>>>>>>> REPLACE
```

Critical rules:
1. SEARCH content must match the associated file section to find EXACTLY:
    * Match character-for-character including whitespace, indentation, line endings
    * Include all comments, docstrings, etc.
2. SEARCH/REPLACE blocks will ONLY replace the first match occurrence.
    * Including multiple unique SEARCH/REPLACE blocks if you need to make multiple changes.
    * Include *just* enough lines in each SEARCH section to uniquely match each set of lines that need to change.
3. Keep SEARCH/REPLACE blocks concise:
    * Break large SEARCH/REPLACE blocks into a series of smaller blocks that each change a small portion of the file.
    * Include just the changing lines, and a few surrounding lines if needed for uniqueness.
    * Do not include long runs of unchanging lines in SEARCH/REPLACE blocks.
4. Special operations:
    * To move code: Use two SEARCH/REPLACE blocks (one to delete from original + one to insert at new location)
    * To delete code: Use empty REPLACE section

Usage:
<replace_in_file>
<path>File path here</path>
<diff>
Search and replace blocks here
</diff>
</replace_in_file>

"""

    def validate_params(self, params: Dict[str, Any]) -> None:
        if "path" not in params:
            raise ValueError("Missing required parameter 'path'")
        if "diff" not in params:
            raise ValueError("Missing required parameter 'diff'")

    def _convert_to_unified_diff(
        self, original_content: str, search_replace_diff: str
    ) -> str:
        """Convert search/replace diff format to unified diff format."""
        # Parse the search/replace blocks
        lines = search_replace_diff.split("\n")
        diff_lines = []
        search_content = []
        replace_content = []
        in_search = False
        in_replace = False

        for line in lines:
            if "<<<<<<< SEARCH" in line:
                in_search = True
            elif "=======" in line:
                in_search = False
                in_replace = True
            elif ">>>>>>> REPLACE" in line:
                # Convert accumulated search/replace block to unified diff format
                if search_content and replace_content:
                    diff_lines.extend(
                        [
                            "--- a/file",
                            "+++ b/file",
                            "@@ -1,{} +1,{} @@".format(
                                len(search_content), len(replace_content)
                            ),
                        ]
                    )
                    diff_lines.extend("-" + line for line in search_content)
                    diff_lines.extend("+" + line for line in replace_content)
                    diff_lines.append("")  # Empty line between hunks
                search_content = []
                replace_content = []
                in_replace = False
            elif in_search:
                search_content.append(line)
            elif in_replace:
                replace_content.append(line)

        return "\n".join(diff_lines)

    def execute(self, params: Dict[str, Any]) -> ToolResult:
        try:
            self.validate_params(params)

            # Read original content
            original_content = FileUtils.read_file(params["path"])

            # Convert search/replace format to unified diff
            unified_diff = self._convert_to_unified_diff(
                original_content, params["diff"]
            )

            # Parse the unified diff
            patch_set = PatchSet(io.StringIO(unified_diff))

            for patch in patch_set:
                for hunk in patch:
                    # Find the matching section in the content
                    source_lines = [
                        line.value
                        for line in hunk
                        if line.is_removed or line.is_context
                    ]
                    source_text = "\n".join(line.rstrip() for line in source_lines)

                    if source_text in original_content:
                        target_lines = [
                            line.value
                            for line in hunk
                            if line.is_added or line.is_context
                        ]
                        target_text = "\n".join(line.rstrip() for line in target_lines)

                        # Replace the content
                        start_pos = original_content.index(source_text)
                        end_pos = start_pos + len(source_text)
                        original_content = (
                            original_content[:start_pos]
                            + target_text
                            + original_content[end_pos:]
                        )

            # Write the modified content
            FileUtils.write_file(params["path"], original_content)

            return ToolResult(
                success=True,
                message=f"Successfully replaced content in file: {params['path']}",
            )

        except Exception as e:
            return ToolResult(
                success=False, message=f"Failed to replace in file: {str(e)}"
            )
