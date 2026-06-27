"""
Kokoro TTS Provider

Fast, local neural TTS.
"""

import os
from typing import AsyncIterator, Dict, Any, Optional

from app.providers.tts.base import TTSProvider, TTSResult
from app.core.logger import get_logger

logger = get_logger(__name__)


class KokoroProvider(TTSProvider):
    name = "kokoro"

    def __init__(self, api_key: Optional[str] = None, voice_id: str = "af_bella", **kwargs):
        super().__init__(api_key, voice_id, **kwargs)
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            from kokoro_onnx import Kokoro
            model_path = self.config.get("model_path", "kokoro-v1.0.onnx")
            voices_path = self.config.get("voices_path", "voices-v1.0.bin")

            if os.path.exists(model_path) and os.path.exists(voices_path):
                self.model = Kokoro(model_path, voices_path)
                logger.info("kokoro.model_loaded")
            else:
                logger.warning("kokoro.model_files_not_found", model_path=model_path, voices_path=voices_path)
        except Exception as e:
            logger.warning("kokoro.load_failed", error=str(e))

    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> TTSResult:
        if self.model is None:
            # Return empty audio with marker
            logger.warning("kokoro.not_loaded", detail="Returning silent audio")
            import struct
            # Minimal WAV header for silence
            silent = b"RIFF\x26\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00\x80\x3e\x00\x00\x00\x7d\x00\x00\x02\x00\x10\x00data\x02\x00\x00\x00\x00\x00"
            return TTSResult(audio_bytes=silent, duration_ms=0)

        import asyncio
        loop = asyncio.get_event_loop()
        vid = voice_id or self.voice_id

        samples, sample_rate = await loop.run_in_executor(
            None,
            lambda: self.model.create(
                text.strip(),
                voice=vid,
                speed=self.config.get("speed", 1.0),
                lang=self.config.get("lang", "en-us"),
            ),
        )

        import wave, io
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            import numpy as np
            audio_int16 = (samples * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())

        duration_ms = int(len(samples) / sample_rate * 1000)
        return TTSResult(
            audio_bytes=buf.getvalue(),
            sample_rate=sample_rate,
            duration_ms=duration_ms,
        )

    async def synthesize_stream(self, text_stream: AsyncIterator[str], voice_id: Optional[str] = None) -> AsyncIterator[TTSResult]:
        """Buffer text and synthesize in chunks."""
        buffer = []
        async for text in text_stream:
            buffer.append(text)
            # Yield every sentence
            if any(c in text for c in ".!?"):
                chunk = " ".join(buffer)
                if chunk.strip():
                    yield await self.synthesize(chunk, voice_id)
                buffer = []

        if buffer:
            chunk = " ".join(buffer)
            if chunk.strip():
                yield await self.synthesize(chunk, voice_id)

    async def healthcheck(self) -> Dict[str, Any]:
        if self.model:
            return {"status": "healthy", "model": "kokoro-v1.0", "voice": self.voice_id}
        return {"status": "degraded", "error": "Model not loaded — check model files"}
