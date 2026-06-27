"""
Voice Pipeline Service

Orchestrates the full voice pipeline:
  Telephony → LiveKit → Pipecat → STT → LLM → Tools → TTS → Audio Out

[MOCKED] The real-time audio loop is stubbed.
The pipeline structure, hooks, and state management are production-ready.
Claude will wire the real-time loop tomorrow.
"""

import uuid
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from app.config import settings
from app.core.logger import get_logger
from app.services.call_session_manager import CallSessionManager, CallSession
from app.services.agent_runtime import AgentRuntime
from app.providers.livekit.adapter import LiveKitAdapter
from app.providers.pipecat.adapter import PipecatAdapter

logger = get_logger(__name__)


class VoicePipelineService:
    """
    High-level voice pipeline orchestrator.

    Manages the full lifecycle of a voice call:
    1. Creates telephony session (Twilio)
    2. Creates LiveKit room for audio transport
    3. Creates Pipecat pipeline for processing
    4. Runs AgentRuntime for LLM + tools
    5. Manages cleanup on hangup
    """

    def __init__(self):
        self.session_manager = CallSessionManager()
        self.livekit = LiveKitAdapter()
        self.pipecat = PipecatAdapter()
        self._active_runtimes: Dict[str, AgentRuntime] = {}

        # Wire Pipecat event hooks
        self.pipecat.on("stt_input", self._on_stt_input)
        self.pipecat.on("llm_input", self._on_llm_input)
        self.pipecat.on("tts_input", self._on_tts_input)
        self.pipecat.on("tool_call", self._on_tool_call)

    async def start_call(
        self,
        agent_id: str,
        agent_config: Dict[str, Any],
        phone_number: Optional[str] = None,
        direction: str = "inbound",
    ) -> Dict[str, Any]:
        """Start a new voice call pipeline."""

        # 1. Create call session
        session = await self.session_manager.create_session(
            agent_id=agent_id,
            phone_number=phone_number,
            direction=direction,
        )

        # 2. Create LiveKit room
        room_name = f"call-{session.call_id}"
        room = await self.livekit.create_room(room_name, identity="agent")

        # 3. Create Pipecat pipeline session
        pipeline_session = await self.pipecat.create_session(
            session_id=session.call_id,
            agent_id=agent_id,
            call_id=session.call_id,
            room_url=room.url,
        )

        # 4. Create AgentRuntime
        runtime = AgentRuntime(agent_id=agent_id, agent_config=agent_config)
        self._active_runtimes[session.call_id] = runtime

        # 5. Start pipeline (mocked)
        await self.pipecat.start_pipeline(session.call_id)
        self.session_manager.update_status(session.call_id, "in_progress")

        logger.info(
            "pipeline.started",
            call_id=session.call_id,
            agent_id=agent_id,
            direction=direction,
        )

        return {
            "call_id": session.call_id,
            "status": "in_progress",
            "room_url": room.url,
            "token": room.token,
            "ws_url": f"{room.url}/ws" if not self.livekit.is_configured() else f"{room.url}",
        }

    async def end_call(self, call_id: str) -> Dict[str, Any]:
        """End a voice call and clean up resources."""
        session = self.session_manager.update_status(call_id, "completed")

        # Stop pipeline
        await self.pipecat.stop_pipeline(call_id)

        # Clean up runtime
        if call_id in self._active_runtimes:
            del self._active_runtimes[call_id]

        # Delete LiveKit room
        room_name = f"call-{call_id}"
        await self.livekit.delete_room(room_name)

        logger.info("pipeline.ended", call_id=call_id)

        return {
            "call_id": call_id,
            "status": "completed",
            "duration_seconds": session.duration_seconds if session else 0,
        }

    async def process_text_turn(self, call_id: str, user_text: str) -> Dict[str, Any]:
        """Process a single text turn (for testing / text-based agents)."""
        runtime = self._active_runtimes.get(call_id)
        if not runtime:
            return {"error": "Call not found or runtime not active", "call_id": call_id}

        response_text = await runtime.on_user_input(user_text)
        self.session_manager.append_transcript(call_id, "user", user_text)
        self.session_manager.append_transcript(call_id, "agent", response_text)

        return {
            "call_id": call_id,
            "response": response_text,
            "turn_count": runtime.turn_count,
        }

    # ── Pipecat Event Handlers ──────────────────────────────────────

    async def _on_stt_input(self, data: Dict):
        """Handle STT input from Pipecat."""
        logger.debug("pipeline.stt_input", session_id=data.get("session_id"))

    async def _on_llm_input(self, data: Dict):
        """Handle LLM input from Pipecat."""
        logger.debug("pipeline.llm_input", session_id=data.get("session_id"))

    async def _on_tts_input(self, data: Dict):
        """Handle TTS input from Pipecat."""
        logger.debug("pipeline.tts_input", session_id=data.get("session_id"))

    async def _on_tool_call(self, data: Dict):
        """Handle tool call from Pipecat."""
        logger.debug("pipeline.tool_call", session_id=data.get("session_id"))

    # ── Health ──────────────────────────────────────────────────────

    async def healthcheck(self) -> Dict[str, Any]:
        lk_health = await self.livekit.healthcheck()
        pc_health = await self.pipecat.healthcheck()
        return {
            "service": "voice_pipeline",
            "livekit": lk_health,
            "pipecat": pc_health,
            "active_calls": len(self._active_runtimes),
        }
