"""
STT Provider Factory
"""

from typing import Optional
from app.config import settings
from app.providers.stt.base import STTProvider
from app.providers.stt.whisper import WhisperProvider

_PROVIDERS = {
    "whisper": WhisperProvider,
}


def get_stt_provider(
    provider_name: Optional[str] = None,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
) -> STTProvider:
    name = (provider_name or settings.STT_PROVIDER).lower()
    cls = _PROVIDERS.get(name)
    if not cls:
        raise ValueError(f"Unknown STT provider: {name}. Available: {list(_PROVIDERS.keys())}")

    return cls(
        api_key=api_key or settings.WHISPER_API_KEY,
        model=model or settings.STT_MODEL,
    )
