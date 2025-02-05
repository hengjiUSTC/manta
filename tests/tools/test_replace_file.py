import os
import unittest
from typing import Any, Dict
from unittest.mock import mock_open, patch

from mantacoder.tools.replace_file import FileUtils, ReplaceFileTool, ToolResult


class TestReplaceFileTool(unittest.TestCase):
    def setUp(self):
        self.tool = ReplaceFileTool()
        self.test_file_path = "test_file.txt"
        self.original_content = """First paragraph with some content
that needs to be replaced.

Second paragraph that also
needs modification.

Third paragraph that should
remain unchanged.

Fourth paragraph that needs
to be updated too."""

    def test_multiple_replacements(self):
        # Prepare multiple search/replace blocks
        diff_content = """<<<<<<< SEARCH
First paragraph with some content
that needs to be replaced.
=======
Updated first paragraph
with new content.
>>>>>>> REPLACE

<<<<<<< SEARCH
Second paragraph that also
needs modification.
=======
Modified second paragraph
with different text.
>>>>>>> REPLACE

<<<<<<< SEARCH
Fourth paragraph that needs
to be updated too.
=======
Final paragraph with
completely new content.
>>>>>>> REPLACE"""

        expected_result = """Updated first paragraph
with new content.

Modified second paragraph
with different text.

Third paragraph that should
remain unchanged.

Final paragraph with
completely new content."""

        # Mock file operations
        with patch.object(
            FileUtils, "read_file", return_value=self.original_content
        ), patch.object(FileUtils, "write_file") as mock_write:
            # Execute the tool
            params = {"path": self.test_file_path, "diff": diff_content}

            result = self.tool.execute(params)

            # Verify the result
            self.assertTrue(result.success)
            mock_write.assert_called_once()
            self.assertEqual(mock_write.call_args[0][1], expected_result)

    def test_invalid_search_content(self):
        # Test with search content that doesn't exist in the file
        diff_content = """<<<<<<< SEARCH
Non-existent content
that isn't in the file
=======
New content that
shouldn't be applied
>>>>>>> REPLACE"""

        # Mock file operations
        with patch.object(
            FileUtils, "read_file", return_value=self.original_content
        ), patch.object(FileUtils, "write_file") as mock_write:
            params = {"path": self.test_file_path, "diff": diff_content}

            result = self.tool.execute(params)

            # The operation should succeed but content should remain unchanged
            self.assertTrue(result.success)
            mock_write.assert_called_once()
            self.assertEqual(mock_write.call_args[0][1], self.original_content)

    def test_overlapping_replacements(self):
        # Test with overlapping search blocks
        diff_content = """<<<<<<< SEARCH
First paragraph with some content
that needs to be replaced.

Second paragraph
=======
New first and second
paragraphs combined.
>>>>>>> REPLACE"""

        # Mock file operations
        with patch.object(
            FileUtils, "read_file", return_value=self.original_content
        ), patch.object(FileUtils, "write_file") as mock_write:
            params = {"path": self.test_file_path, "diff": diff_content}

            result = self.tool.execute(params)

            # Verify the result
            self.assertTrue(result.success)
            mock_write.assert_called_once()


if __name__ == "__main__":
    unittest.main()
