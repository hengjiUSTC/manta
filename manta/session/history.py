from dataclasses import dataclass, field
from typing import Dict, List

import tiktoken


@dataclass
class ConversationHistory:
    """Manages conversation history."""

    messages: List[Dict[str, str]] = field(default_factory=list)
    max_tokens: int = 32000  # Default max token limit, can be adjusted
    encoding: tiktoken.Encoding = tiktoken.get_encoding("cl100k_base")

    def add_system_message(self, system_prompt: str) -> None:
        """Initialize with system prompt."""
        self.messages.append({"role": "system", "content": system_prompt})

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the history and ensure it doesn't exceed max tokens."""
        self.messages.append({"role": role, "content": content})
        self._truncate_history_if_needed()

    def get_context(self) -> List[Dict[str, str]]:
        """Get current conversation context."""
        return self.messages.copy()

    def get_total_tokens(self) -> int:
        """Get the total token count for the current messages."""
        return self._calculate_total_tokens()

    def clear(self) -> None:
        """Clear conversation history except system prompt."""
        self.messages = [self.messages[0]]  # Keep system prompt

    def _truncate_history_if_needed(self) -> None:
        """Ensure the total token count remains within the limit."""
        while self._calculate_total_tokens() > self.max_tokens:
            # Remove the first non-system message
            for i, message in enumerate(self.messages):
                if message["role"] != "system":
                    del self.messages[i]
                    break

    def _calculate_total_tokens(self) -> int:
        """Calculate the total token count for the current messages."""
        total_tokens = 0
        for message in self.messages:
            content = message["content"]
            total_tokens += len(self.encoding.encode(content))
        return total_tokens
