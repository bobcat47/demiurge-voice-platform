"""
LLM Provider Abstract Base

All LLM backends (OpenRouter, Gemini, Groq, OpenAI) implement this interface.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class LLMMessage:
    role: str  # system | user | assistant | tool
    content: str
    tool_calls: Optional[List[Dict]] = None
    tool_results: Optional[List[Dict]] = None


@dataclass
class LLMResponse:
    content: str
    tool_calls: List[Dict] = None
    usage: Dict[str, int] = None
    model: str = ""
    finish_reason: str = ""

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []
        if self.usage is None:
            self.usage = {}


class LLMProvider(ABC):
    """Abstract base for all LLM providers."""

    name: str = "abstract"

    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs

    @abstractmethod
    async def complete(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Send a completion request."""
        pass

    @abstractmethod
    async def stream(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream completion tokens."""
        pass

    @abstractmethod
    async def healthcheck(self) -> Dict[str, Any]:
        """Return provider health status."""
        pass

    def format_tools(self, tools: List[Dict]) -> List[Dict]:
        """Convert internal tool schema to provider-specific format. Override if needed."""
        return tools
