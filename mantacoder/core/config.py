# code_agent/core/config.py
from dataclasses import dataclass


@dataclass
class Config:
    """Configuration for the code agent."""

    api_key: str
    base_url: str
    model: str
    name: str = "Manta"
