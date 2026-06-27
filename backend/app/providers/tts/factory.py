"""
TTS Provider Factory
"""

from typing import Optional
from app.config import settings
from app.providers.tts.base import TTSProvider
from app.providers.tts.kokoro import KokoroProvider
from app.providers.tts.piper import PiperProvider

_PROVIDERS = {
    "kokoro": KokoroProvider,
    "piper": PiperProvider,
}


def get_tts_provider(
    provider_name: Optional[str] = None,
    voice_id: Optional[str] = None,
) -> TTSProvider:
    name = (provider_name or settings.TTS_PROVIDER).lower()
    cls = _PROVIDERS.get(name)
    if not cls:
        raise ValueError(f"Unknown TTS provider: {name}. Available: {list(_PROVIDERS.keys())}")

    return cls(
        voice_id=voice_id or settings.TTS_VOICE,
    )
