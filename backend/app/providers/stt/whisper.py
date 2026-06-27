"""
Whisper STT Provider

Uses faster-whisper locally or OpenAI Whisper API.
"""

import os
import tempfile
from typing import AsyncIterator, Dict, Any, Optional

from app.providers.stt.base import STTProvider, TranscriptionResult
from app.core.logger import get_logger

logger = get_logger(__name__)


class WhisperProvider(STTProvider):
    name = "whisper"

    def __init__(self, api_key: Optional[str] = None, model: str = "base", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.local = kwargs.get("local", True)
        self.local_model = None

        if self.local:
            try:
                from faster_whisper import WhisperModel
                device = kwargs.get("device", "cpu")
                compute_type = kwargs.get("compute_type", "int8")
                self.local_model = WhisperModel(model, device=device, compute_type=compute_type)
                logger.info("whisper.local_model_loaded", model=model, device=device)
            except Exception as e:
                logger.warning("whisper.local_load_failed", error=str(e), fallback="api")
                self.local = False

    async def transcribe(self, audio_bytes: bytes, language: Optional[str] = None) -> TranscriptionResult:
        if self.local and self.local_model:
            return await self._transcribe_local(audio_bytes, language)
        return await self._transcribe_api(audio_bytes, language)

    async def _transcribe_local(self, audio_bytes: bytes, language: Optional[str] = None) -> TranscriptionResult:
        import asyncio
        loop = asyncio.get_event_loop()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            tmp_path = f.name

        try:
            segments, info = await loop.run_in_executor(
                None,
                lambda: self.local_model.transcribe(tmp_path, language=language, beam_size=5),
            )
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)
            return TranscriptionResult(
                text=" ".join(text_parts).strip(),
                language=info.language,
                confidence=1.0,
            )
        finally:
            os.unlink(tmp_path)

    async def _transcribe_api(self, audio_bytes: bytes, language: Optional[str] = None) -> TranscriptionResult:
        import httpx
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
        data = {"model": "whisper-1"}
        if language:
            data["language"] = language

        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers=headers,
                files=files,
                data=data,
            )
            resp.raise_for_status()
            result = resp.json()
            return TranscriptionResult(
                text=result.get("text", ""),
                language=language,
                confidence=1.0,
            )

    async def transcribe_stream(self, audio_stream: AsyncIterator[bytes], language: Optional[str] = None) -> AsyncIterator[TranscriptionResult]:
        """Stream transcription — collects chunks and transcribes periodically."""
        import asyncio
        buffer = bytearray()
        chunk_count = 0

        async for chunk in audio_stream:
            buffer.extend(chunk)
            chunk_count += 1

            # Transcribe every ~3 seconds of audio (approx 48k bytes at 8kHz 16bit)
            if len(buffer) > 48000 * 3:
                result = await self.transcribe(bytes(buffer), language)
                result.is_final = False
                yield result
                buffer = bytearray()

        if buffer:
            result = await self.transcribe(bytes(buffer), language)
            result.is_final = True
            yield result

    async def healthcheck(self) -> Dict[str, Any]:
        if self.local and self.local_model:
            return {"status": "healthy", "mode": "local", "model": self.model}
        if self.api_key:
            return {"status": "healthy", "mode": "api"}
        return {"status": "down", "error": "No local model or API key"}
