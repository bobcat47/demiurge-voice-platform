"""
Call Summary Service

Generates summaries of call transcripts using LLM.
"""

from typing import Dict, Any, List, Optional

from app.providers.llm.base import LLMProvider, LLMMessage
from app.providers.llm.factory import get_llm_provider
from app.core.logger import get_logger

logger = get_logger(__name__)


SUMMARY_PROMPT = """You are a call summary assistant. Analyze the following call transcript and provide:
1. A concise summary (2-3 sentences)
2. Key points discussed (bullet list)
3. Overall sentiment (positive / neutral / negative)
4. Action items (if any)

Format your response as JSON with keys: summary, key_points, sentiment, action_items

Transcript:
{transcript}
"""


class CallSummaryService:
    """Generates AI-powered call summaries."""

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider or get_llm_provider()

    async def summarize(self, transcript: str) -> Dict[str, Any]:
        """Generate a summary of a call transcript."""
        if not transcript or not transcript.strip():
            return {
                "summary": "No transcript available.",
                "key_points": [],
                "sentiment": "neutral",
                "action_items": [],
            }

        prompt = SUMMARY_PROMPT.format(transcript=transcript)
        messages = [LLMMessage(role="user", content=prompt)]

        try:
            response = await self.llm.complete(messages, temperature=0.3)
            content = response.content or "{}"

            # Try to parse as JSON
            import json
            try:
                result = json.loads(content)
                return {
                    "summary": result.get("summary", content[:500]),
                    "key_points": result.get("key_points", []),
                    "sentiment": result.get("sentiment", "neutral"),
                    "action_items": result.get("action_items", []),
                }
            except json.JSONDecodeError:
                # Fallback: return raw content as summary
                return {
                    "summary": content[:1000],
                    "key_points": [],
                    "sentiment": "neutral",
                    "action_items": [],
                }
        except Exception as e:
            logger.error("call_summary.failed", error=str(e))
            return {
                "summary": "Summary generation failed.",
                "key_points": [],
                "sentiment": "neutral",
                "action_items": [],
                "error": str(e),
            }
