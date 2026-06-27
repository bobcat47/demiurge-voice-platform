"""
Demiurge Voice Platform — Provider Abstractions

All provider implementations are registered here.
The platform never hardcodes a specific provider.
"""

from app.providers.llm.base import LLMProvider
from app.providers.stt.base import STTProvider
from app.providers.tts.base import TTSProvider
from app.providers.telephony.base import TelephonyProvider

__all__ = ["LLMProvider", "STTProvider", "TTSProvider", "TelephonyProvider"]
