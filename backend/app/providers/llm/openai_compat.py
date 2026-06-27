"""
OpenAI-Compatible LLM Provider

Works with any OpenAI-compatible endpoint (Ollama, vLLM, etc.)
"""

import httpx
from typing import AsyncIterator, List, Dict, Any, Optional

from app.providers.llm.base import LLMProvider, LLMMessage, LLMResponse
from app.core.logger import get_logger

logger = get_logger(__name__)


class OpenAICompatProvider(LLMProvider):
    name = "openai_compat"

    def __init__(self, api_key: str, model: str, **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = kwargs.get("base_url", "https://api.openai.com/v1")
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

    def _format_messages(self, messages: List[LLMMessage]) -> List[Dict]:
        return [{"role": m.role, "content": m.content} for m in messages]

    async def complete(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        payload = {
            "model": self.model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                choice = data["choices"][0]
                return LLMResponse(
                    content=choice["message"].get("content", ""),
                    tool_calls=choice["message"].get("tool_calls", []),
                    usage=data.get("usage", {}),
                    model=data.get("model", self.model),
                    finish_reason=choice.get("finish_reason", ""),
                )
            except Exception as e:
                logger.error("openai_compat.complete_failed", error=str(e))
                raise

    async def stream(
        self,
        messages: List[LLMMessage],
        tools: Optional[List[Dict]] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        payload = {
            "model": self.model,
            "messages": self._format_messages(messages),
            "temperature": temperature,
            "stream": True,
        }
        if max_tokens:
            payload["max_tokens"] = max_tokens

        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload,
            ) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        chunk = line[6:]
                        if chunk == "[DONE]":
                            break
                        try:
                            import json
                            data = json.loads(chunk)
                            delta = data["choices"][0]["delta"].get("content", "")
                            if delta:
                                yield delta
                        except Exception:
                            pass

    async def healthcheck(self) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{self.base_url}/models",
                    headers=self.headers,
                )
                if resp.status_code == 200:
                    return {"status": "healthy", "latency_ms": resp.elapsed.total_seconds() * 1000}
                return {"status": "degraded", "error": f"HTTP {resp.status_code}"}
        except Exception as e:
            return {"status": "down", "error": str(e)}
