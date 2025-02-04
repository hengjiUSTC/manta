import logging
from typing import Dict, List

from openai import OpenAI

from manta.core.config import Config
from manta.core.exceptions import LLMError

logging.getLogger("httpx").setLevel(logging.WARNING)


class LLMClient:
    """OpenAI API client wrapper."""

    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(api_key=config.api_key, base_url=config.base_url)

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Send a chat request to the API."""
        try:
            response = self.client.chat.completions.create(
                model=self.config.model, messages=messages, max_tokens=8000
            )
            return response.choices[0].message.content
        except Exception as e:
            raise LLMError(f"Failed to get LLM response: {e}")
