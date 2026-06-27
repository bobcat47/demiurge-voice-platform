"""
Google Gemini LLM Provider

Native Gemini API (not via OpenRouter).
"""

import httpx
from typing import AsyncIterator, List, Dict, Any, Optional

from app.providers.llm.base import LLMProvider, LLMMessage, LLMResponse
from app.core.logger import get_logger

logger = get_logger(__name__)


class GeminiProvider(LLMProvider):
    name = "gemini"
    base_url = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, api_key: str, model: str, **kwargs):
        # Normalize model name
        if not model.startswith("models/") and "/" not in model:
            model = f"models/{model}"
        super().__init__(api_key, model, **kwargs)

    def _format_messages(self, messages: List[LLMMessage]) -> List[Dict]:
        """Convert to Gemini's contents format."""
        contents = []
        for m in messages:
            role = "model" if m.role == "assistant" else m.role
            contents.append({"role": role, "parts": [{"text": m.content}]})
        return contents

    async def complete(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "contents": self._format_messages(messages),
            "generationConfig": {"temperature": temperature},
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                candidate = data["candidates"][0]
                content = candidate["content"]["parts"][0].get("text", "")
                return LLMResponse(
                    content=content,
                    model=self.model,
                    finish_reason=candidate.get("finishReason", ""),
                )
            except Exception as e:
                logger.error("gemini.complete_failed", error=str(e))
                raise

    async def stream(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        url = f"{self.base_url}/{self.model}:streamGenerateContent?alt=sse&key={self.api_key}"
        payload = {
            "contents": self._format_messages(messages),
            "generationConfig": {"temperature": temperature},
        }
        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            import json
                            data = json.loads(line[6:])
                            text = data["candidates"][0]["content"]["parts"][0].get("text", "")
                            if text:
                                yield text
                        except Exception:
                            pass

    async def healthcheck(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/models?key={self.api_key}"
                )
                if resp.status_code == 200:
                    return {"status": "healthy", "latency_ms": resp.elapsed.total_seconds() * 1000}
                return {"status": "degraded", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "down", "error": str(e)}
