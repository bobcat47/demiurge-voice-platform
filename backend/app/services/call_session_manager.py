"""
Call Session Manager

Manages the lifecycle of voice call sessions.
Tracks state, participants, timing, and metadata.
"""

import uuid
from typing import Dict, Optional, List
from datetime import datetime, timezone
from dataclasses import dataclass, field

from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class CallSession:
    call_id: str
    agent_id: str
    phone_number: Optional[str] = None
    direction: str = "inbound"
    status: str = "queued"  # queued | ringing | in_progress | completed | failed | cancelled
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    duration_seconds: int = 0
    transcript: str = ""
    recording_url: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


class CallSessionManager:
    """In-memory call session tracker.
    
    [NOTE] For production at scale, persist to PostgreSQL via Call model.
    """

    def __init__(self):
        self._sessions: Dict[str, CallSession] = {}

    async def create_session(
        self,
        agent_id: str,
        phone_number: Optional[str] = None,
        direction: str = "inbound",
        metadata: Optional[Dict] = None,
    ) -> CallSession:
        call_id = str(uuid.uuid4())
        session = CallSession(
            call_id=call_id,
            agent_id=agent_id,
            phone_number=phone_number,
            direction=direction,
            status="queued",
            metadata=metadata or {},
        )
        self._sessions[call_id] = session
        logger.info("session.created", call_id=call_id, agent_id=agent_id, direction=direction)
        return session

    def get_session(self, call_id: str) -> Optional[CallSession]:
        return self._sessions.get(call_id)

    def update_status(self, call_id: str, status: str) -> Optional[CallSession]:
        session = self._sessions.get(call_id)
        if not session:
            return None
        session.status = status
        if status == "in_progress" and not session.started_at:
            session.started_at = datetime.now(timezone.utc)
        if status in ("completed", "failed", "cancelled") and not session.ended_at:
            session.ended_at = datetime.now(timezone.utc)
            if session.started_at:
                session.duration_seconds = int((session.ended_at - session.started_at).total_seconds())
        logger.info("session.status_updated", call_id=call_id, status=status)
        return session

    def append_transcript(self, call_id: str, speaker: str, text: str) -> None:
        session = self._sessions.get(call_id)
        if session:
            entry = f"[{speaker}] {text}\n"
            session.transcript += entry

    def list_sessions(
        self,
        agent_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> List[CallSession]:
        sessions = list(self._sessions.values())
        if agent_id:
            sessions = [s for s in sessions if s.agent_id == agent_id]
        if status:
            sessions = [s for s in sessions if s.status == status]
        sessions.sort(key=lambda s: s.started_at or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
        return sessions[:limit]

    async def end_session(self, call_id: str) -> Optional[CallSession]:
        return self.update_status(call_id, "completed")

    def cleanup_old_sessions(self, max_age_hours: int = 24) -> int:
        """Remove completed sessions older than max_age_hours."""
        now = datetime.now(timezone.utc)
        to_remove = []
        for call_id, session in self._sessions.items():
            if session.status in ("completed", "failed", "cancelled"):
                if session.ended_at and (now - session.ended_at).total_seconds() > max_age_hours * 3600:
                    to_remove.append(call_id)
        for call_id in to_remove:
            del self._sessions[call_id]
        logger.info("session.cleanup", removed=len(to_remove))
        return len(to_remove)
