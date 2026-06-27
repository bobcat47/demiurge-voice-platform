"""
STT (Speech-to-Text) Provider Abstract Base
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    text: str
    language: Optional[str] = None
    confidence: float = 0.0
    word_timings: Optional[list] = None
    is_final: bool = True


class STTProvider(ABC):
    name: str = "abstract"

    def __init__(self, api_key: Optional[str] = None, model: str = "base", **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs

    @abstractmethod
    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> TranscriptionResult:
        """Transcribe audio bytes to text."""
        pass

    @abstractmethod
    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes], language: Optional[str] = None) -> AsyncIterator[TranscriptionResult]:
        """Stream transcription from audio chunks."""
        pass

    @abstractmethod
    async def healthcheck(self) -> Dict[str, Any]:
        pass
