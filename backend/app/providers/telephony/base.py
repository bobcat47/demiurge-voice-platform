"""
Telephony Provider Abstract Base
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class CallRequest:
    to_number: str
    from_number: Optional[str] = None
    agent_id: Optional[str] = None
    webhook_url: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CallResult:
    call_sid: str
    status: str
    direction: str
    from_number: Optional[str] = None
    to_number: Optional[str] = None
    error: Optional[str] = None


class TelephonyProvider(ABC):
    name: str = "abstract"

    @abstractmethod
    async def make_call(self, request: CallRequest) -> CallResult:
        pass

    @abstractmethod
    async def end_call(self, call_sid: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming webhooks from the telephony provider."""
        pass

    @abstractmethod
    async def healthcheck(self) -> Dict[str, Any]:
        pass
