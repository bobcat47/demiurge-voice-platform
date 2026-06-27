"""
Transcript Store

Manages transcript persistence and retrieval.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone

from app.core.logger import get_logger

logger = get_logger(__name__)


class TranscriptStore:
    """Simple transcript storage.
    
    [NOTE] For production, persist to PostgreSQL via Call model.
    """

    def __init__(self):
        self._transcripts: Dict[str, str] = {}

    def save(self, call_id: str, transcript: str) -> None:
        self._transcripts[call_id] = transcript
        logger.info("transcript.saved", call_id=call_id, length=len(transcript))

    def get(self, call_id: str) -> Optional[str]:
        return self._transcripts.get(call_id)

    def append(self, call_id: str, speaker: str, text: str) -> None:
        entry = f"[{speaker}] {text}\n"
        if call_id not in self._transcripts:
            self._transcripts[call_id] = ""
        self._transcripts[call_id] += entry

    def get_formatted(self, call_id: str) -> str:
        return self._transcripts.get(call_id, "")
