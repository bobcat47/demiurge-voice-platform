"""
LLM Provider Factory

Instantiates the correct LLM provider based on configuration.
"""

from typing import Optional
from app.config import settings
from app.providers.llm.base import LLMProvider
from app.providers.llm.openrouter import OpenRouterProvider
from app.providers.llm.gemini import GeminiProvider
from app.providers.llm.groq import GroqProvider
from app.providers.llm.openai_compat import OpenAICompatProvider


_PROVIDERS = {
    "openrouter": OpenRouterProvider,
    "gemini": GeminiProvider,
    "groq": GroqProvider,
    "openai": OpenAICompatProvider,
    "openai_compat": OpenAICompatProvider,
}


def get_llm_provider(
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> LLMProvider:
    """Factory: create LLM provider from config or overrides."""
    name = (provider_name or settings.LLM_PROVIDER).lower()
    cls = _PROVIDERS.get(name)
    if not cls:
        raise ValueError(f"Unknown LLM provider: {name}. Available: {list(_PROVIDERS.keys())}")

    # Resolve API key
    if api_key:
        key = api_key
    elif name == "openrouter":
        key = settings.OPENROUTER_API_KEY
    elif name == "gemini":
        key = settings.GEMINI_API_KEY
    elif name == "groq":
        key = settings.GROQ_API_KEY
    elif name in ("openai", "openai_compat"):
        key = settings.OPENAI_API_KEY
    else:
        key = None

    if not key:
        raise ValueError(f"No API key configured for LLM provider: {name}")

    return cls(
        api_key=key,
        model=model or settings.LLM_MODEL,
    )


def list_available_providers() -> list:
    """Return available provider names and their status."""
    result = []
    for name, cls in _PROVIDERS.items():
        key = None
        if name == "openrouter":
            key = settings.OPENROUTER_API_KEY
        elif name == "gemini":
            key = settings.GEMINI_API_KEY
        elif name == "groq":
            key = settings.GROQ_API_KEY
        elif name == "openai":
            key = settings.OPENAI_API_KEY
        result.append({
            "name": name,
            "class": cls.__name__,
            "configured": key is not None and len(key) > 0,
        })
    return result
