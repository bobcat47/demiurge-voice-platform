"""
Piper TTS Provider

Lightweight local neural TTS.
"""

import os
import subprocess
import tempfile
from typing import AsyncIterator, Dict, Any, Optional

from app.providers.tts.base import TTSProvider, TTSResult
from app.core.logger import get_logger

logger = get_logger(__name__)


class PiperProvider(TTSProvider):
    name = "piper"

    def __init__(self, api_key: Optional[str] = None, voice_id: str = "en_US-lessac-medium", **kwargs):
        super().__init__(api_key, voice_id, **kwargs)
        self.model_path = kwargs.get("model_path", f"{voice_id}.onnx")
        self.piper_binary = kwargs.get("piper_binary", "piper")
        self._check_binary()

    def _check_binary(self):
        try:
            subprocess.run([self.piper_binary, "--help"], capture_output=True, check=True)
            self.binary_available = True
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.binary_available = False
            logger.warning("piper.binary_not_found", binary=self.piper_binary)

    async def synthesize(self, text: str, voice_id: Optional[str] = None) -> TTSResult:
        if not self.binary_available:
            return TTSResult(audio_bytes=b"", duration_ms=0)

        import asyncio
        vid = voice_id or self.voice_id
        model = self.config.get("model_path", f"{vid}.onnx")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as tf:
            tf.write(text.strip())
            text_path = tf.name

        wav_path = text_path.replace(".txt", ".wav")

        try:
            proc = await asyncio.create_subprocess_exec(
                self.piper_binary,
                "--model", model,
                "--config", model.replace(".onnx", ".onnx.json"),
                "--file", text_path,
                "--output_file", wav_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()

            if os.path.exists(wav_path):
                with open(wav_path, "rb") as f:
                    audio = f.read()
                # Estimate duration from file size (16-bit mono @ 22050Hz)
                duration_ms = int((len(audio) - 44) / 2 / 22050 * 1000) if len(audio) > 44 else 0
                return TTSResult(audio_bytes=audio, sample_rate=22050, duration_ms=duration_ms)
            return TTSResult(audio_bytes=b"", duration_ms=0)
        finally:
            for p in [text_path, wav_path]:
                if os.path.exists(p):
                    os.unlink(p)

    async def synthesize_stream(self, text_stream: AsyncIterator[str], voice_id: Optional[str] = None) -> AsyncIterator[TTSResult]:
        buffer = []
        async for text in text_stream:
            buffer.append(text)
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
        if self.binary_available:
            return {"status": "healthy", "binary": self.piper_binary, "voice": self.voice_id}
        return {"status": "degraded", "error": f"Piper binary not found: {self.piper_binary}"}
