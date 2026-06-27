"""
TTS (Text-to-Speech) Provider Abstract Base
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TTSResult:
    audio_bytes: bytes
    sample_rate: int = 24000
    format: str = "wav"
    duration_ms: int = 0


class TTSProvider(ABC):
    name: str = "abstract"

    def __init__(self, api_key: Optional[str] = None, voice_id: str = "default", **kwargs):
        self.api_key = api_key
        self.voice_id = voice_id
        self.config = kwargs

    @abstractmethod
    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> TTSResult:
        """Convert text to speech audio bytes."""
        pass

    @abstractmethod
    async def synthesize_stream(self, text_stream: AsyncIterator[str], voice_id: Optional[str] = None) -> AsyncIterator[TTSResult]:
        """Stream text to speech chunks."""
        pass

    @abstractmethod
    async def healthcheck(self) -> Dict[str, Any]:
        pass
