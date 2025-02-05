from dataclasses import dataclass, field
from typing import Dict, List

import tiktoken


@dataclass
class ConversationHistory:
    """Manages conversation history with efficient token counting."""

    messages: List[Dict[str, str]] = field(default_factory=list)
    max_tokens: int = 32000  # Default max token limit
    encoding: tiktoken.Encoding = field(
        default_factory=lambda: tiktoken.get_encoding("cl100k_base")
    )
    _token_counts: Dict[int, int] = field(
        default_factory=dict
    )  # Cache for token counts
    _total_tokens: int = field(default=0)  # Running total of tokens

    def _count_tokens(self, content: str) -> int:
        """Count tokens for a given content string."""
        return len(self.encoding.encode(content))

    def add_system_message(self, system_prompt: str) -> None:
        """Initialize with system prompt."""
        token_count = self._count_tokens(system_prompt)
        self.messages.append({"role": "system", "content": system_prompt})
        self._token_counts[0] = token_count
        self._total_tokens += token_count

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the history and ensure it doesn't exceed max tokens."""
        token_count = self._count_tokens(content)
        message_index = len(self.messages)

        self.messages.append({"role": role, "content": content})
        self._token_counts[message_index] = token_count
        self._total_tokens += token_count

        self._truncate_history_if_needed()

    def get_context(self) -> List[Dict[str, str]]:
        """Get current conversation context."""
        return self.messages.copy()

    def get_total_tokens(self) -> int:
        """Get the total token count for the current messages."""
        return self._total_tokens

    def get_max_tokens(self) -> int:
        """Get the maximum token limit."""
        return self.max_tokens

    def clear(self) -> None:
        """Clear conversation history except system prompt."""
        system_tokens = self._token_counts[0]  # Save system prompt token count
        self.messages = [self.messages[0]]  # Keep system prompt
        self._token_counts = {0: system_tokens}  # Reset token counts
        self._total_tokens = system_tokens  # Reset total tokens

    def _truncate_history_if_needed(self) -> None:
        """Ensure the total token count remains within the limit."""
        while self._total_tokens > self.max_tokens:
            # Find first non-system message
            for i, message in enumerate(self.messages):
                if message["role"] != "system":
                    # Subtract tokens for the message being removed
                    self._total_tokens -= self._token_counts[i]

                    # Remove the message and its token count
                    del self.messages[i]
                    del self._token_counts[i]

                    # Update indices in token_counts for remaining messages
                    new_counts = {}
                    for old_idx, count in self._token_counts.items():
                        if old_idx < i:
                            new_counts[old_idx] = count
                        elif old_idx > i:
                            new_counts[old_idx - 1] = count
                    self._token_counts = new_counts
                    break
