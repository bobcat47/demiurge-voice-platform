"""
Pipecat Adapter

Wraps Pipecat for voice pipeline orchestration.
MARKED: Full pipeline is MOCKED — will be wired by Claude tomorrow.
"""

import asyncio
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PipelineFrame:
    frame_type: str  # audio_in | transcription | llm_response | tts_audio | tool_call | control
    data: Any
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PipelineSession:
    session_id: str
    agent_id: str
    call_id: str
    status: str = "created"  # created | running | paused | ended
    frames_processed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class PipecatAdapter:
    """
    Pipecat voice pipeline adapter.

    [MOCKED] The full Pipecat pipeline integration will be wired by Claude Code.
    Current implementation provides:
    - Pipeline session lifecycle management
    - Frame-based processing abstraction
    - Pipeline stage hooks
    - Placeholder for Transport, STT, TTS, LLM processors
    """

    def __init__(self):
        self._sessions: Dict[str, PipelineSession] = {}
        self._hooks: Dict[str, List[Callable]] = {}
        self._pipecat_available = False

        try:
            import pipecat
            self._pipecat_available = True
            logger.info("pipecat.sdk_available", version=getattr(pipecat, "__version__", "unknown"))
        except ImportError:
            logger.warning("pipecat.sdk_not_installed", detail="Running in mock mode")

    def is_available(self) -> bool:
        return self._pipecat_available

    async def create_session(
        self,
        session_id: str,
        agent_id: str,
        call_id: str,
        room_url: Optional[str] = None,
    ) -> PipelineSession:
        """Create a new pipeline session."""
        session = PipelineSession(
            session_id=session_id,
            agent_id=agent_id,
            call_id=call_id,
            status="created",
            metadata={"room_url": room_url},
        )
        self._sessions[session_id] = session
        logger.info("pipecat.session_created", session_id=session_id, agent_id=agent_id)
        return session

    async def start_pipeline(self, session_id: str) -> bool:
        """Start the voice pipeline for a session."""
        session = self._sessions.get(session_id)
        if not session:
            logger.error("pipecat.session_not_found", session_id=session_id)
            return False

        session.status = "running"
        session.start_time = datetime.now(timezone.utc)
        logger.info("pipecat.pipeline_started", session_id=session_id)

        # Emit pipeline started event
        await self.emit("pipeline_started", {"session_id": session_id})

        # [MOCKED] In full implementation, this would:
        # 1. Create Daily/WebRTC transport
        # 2. Add STT processor (Whisper/Deepgram)
        # 3. Add LLM processor (OpenRouter/Gemini)
        # 4. Add TTS processor (Kokoro/Piper)
        # 5. Add tool executor
        # 6. Run the pipeline

        return True

    async def process_frame(self, session_id: str, frame: PipelineFrame) -> Optional[PipelineFrame]:
        """Process a single frame through the pipeline."""
        session = self._sessions.get(session_id)
        if not session or session.status != "running":
            return None

        session.frames_processed += 1

        # Route frame based on type
        if frame.frame_type == "audio_in":
            # [MOCKED] Would go to STT
            await self.emit("stt_input", {"session_id": session_id, "audio": frame.data})
            return PipelineFrame(frame_type="transcription", data="[Transcribed text would appear here]")

        elif frame.frame_type == "transcription":
            # [MOCKED] Would go to LLM
            await self.emit("llm_input", {"session_id": session_id, "text": frame.data})
            return PipelineFrame(frame_type="llm_response", data="[LLM response would appear here]")

        elif frame.frame_type == "llm_response":
            # [MOCKED] Would go to TTS
            await self.emit("tts_input", {"session_id": session_id, "text": frame.data})
            return PipelineFrame(frame_type="tts_audio", data=b"[Audio bytes would appear here]")

        elif frame.frame_type == "tool_call":
            # [MOCKED] Would execute tool
            await self.emit("tool_call", {"session_id": session_id, "tool": frame.data})
            return PipelineFrame(frame_type="control", data="tool_executed")

        return None

    async def stop_pipeline(self, session_id: str) -> bool:
        """Stop the pipeline for a session."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        session.status = "ended"
        session.end_time = datetime.now(timezone.utc)
        logger.info("pipecat.pipeline_stopped", session_id=session_id)
        await self.emit("pipeline_ended", {"session_id": session_id})
        return True

    def get_session(self, session_id: str) -> Optional[PipelineSession]:
        return self._sessions.get(session_id)

    def on(self, event: str, callback: Callable):
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)

    async def emit(self, event: str, data: Any):
        for cb in self._hooks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(data)
                else:
                    cb(data)
            except Exception as e:
                logger.error("pipecat.hook_error", event=event, error=str(e))

    async def healthcheck(self) -> Dict[str, Any]:
        return {
            "status": "available" if self._pipecat_available else "mocked",
            "sdk_installed": self._pipecat_available,
            "active_sessions": len([s for s in self._sessions.values() if s.status == "running"]),
        }
