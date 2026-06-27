"""
LiveKit Adapter

Wraps LiveKit for room/session management.
MARKED: Core real-time audio loop is MOCKED — will be wired by Claude tomorrow.
"""

import asyncio
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone

from app.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class LiveKitRoom:
    room_name: str
    token: str
    url: str
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    participants: list = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LiveKitAdapter:
    """
    LiveKit integration adapter.

    [MOCKED] The full real-time audio pipeline will be wired by Claude Code
    in the next iteration. Current implementation provides:
    - Room creation / token generation
    - Participant tracking
    - WebSocket URL generation
    - Event hooks for pipeline stages
    """

    def __init__(self):
        self.url = settings.LIVEKIT_URL
        self.api_key = settings.LIVEKIT_API_KEY
        self.api_secret = settings.LIVEKIT_API_SECRET
        self._rooms: Dict[str, LiveKitRoom] = {}
        self._hooks: Dict[str, list] = {}

        if not all([self.url, self.api_key, self.api_secret]):
            logger.warning("livekit.not_configured", detail="Running in mock mode")
            self._mock_mode = True
        else:
            self._mock_mode = False
            try:
                from livekit import api
                self._api = api
            except ImportError:
                logger.warning("livekit.sdk_not_installed", detail="Running in mock mode")
                self._mock_mode = True

    def is_configured(self) -> bool:
        return not self._mock_mode

    async def create_room(self, room_name: str, identity: str = "agent") -> LiveKitRoom:
        """Create a LiveKit room and generate an access token."""
        if self._mock_mode:
            room = LiveKitRoom(
                room_name=room_name,
                token=f"mock_token_{room_name}",
                url=self.url or "wss://mock.livekit.cloud",
            )
            self._rooms[room_name] = room
            return room

        # Live SDK path
        token = self._api.AccessToken(self.api_key, self.api_secret)
        token.with_identity(identity)
        token.with_name("Demiurge Agent")
        grant = self._api.VideoGrant(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        )
        token.with_grant(grant)
        jwt = token.to_jwt()

        room = LiveKitRoom(
            room_name=room_name,
            token=jwt,
            url=self.url,
        )
        self._rooms[room_name] = room
        logger.info("livekit.room_created", room_name=room_name)
        return room

    async def delete_room(self, room_name: str) -> bool:
        if room_name in self._rooms:
            del self._rooms[room_name]
        if not self._mock_mode:
            try:
                svc = self._api.RoomService(self.url, self.api_key, self.api_secret)
                await svc.delete_room(self._api.DeleteRoomRequest(room=room_name))
            except Exception as e:
                logger.error("livekit.delete_room_failed", error=str(e))
        logger.info("livekit.room_deleted", room_name=room_name)
        return True

    def get_room(self, room_name: str) -> Optional[LiveKitRoom]:
        return self._rooms.get(room_name)

    def on(self, event: str, callback: Callable):
        """Register an event hook. Events: participant_joined, audio_frame, disconnect"""
        if event not in self._hooks:
            self._hooks[event] = []
        self._hooks[event].append(callback)

    async def emit(self, event: str, data: Any):
        """Emit an event to all registered hooks."""
        for cb in self._hooks.get(event, []):
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(data)
                else:
                    cb(data)
            except Exception as e:
                logger.error("livekit.hook_error", event=event, error=str(e))

    async def healthcheck(self) -> Dict[str, Any]:
        if self._mock_mode:
            return {"status": "mocked", "configured": False}
        try:
            svc = self._api.RoomService(self.url, self.api_key, self.api_secret)
            await svc.list_rooms(self._api.ListRoomsRequest())
            return {"status": "healthy", "configured": True, "url": self.url}
        except Exception as e:
            return {"status": "degraded", "error": str(e)}
