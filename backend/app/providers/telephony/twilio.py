"""
Twilio Telephony Provider
"""

from typing import Dict, Any, Optional
from twilio.rest import Client as TwilioClient
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

from app.providers.telephony.base import TelephonyProvider, CallRequest, CallResult
from app.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class TwilioProvider(TelephonyProvider):
    name = "twilio"

    def __init__(self):
        self.client = None
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = TwilioClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            self.phone_number = settings.TWILIO_PHONE_NUMBER

    async def make_call(self, request: CallRequest) -> CallResult:
        if not self.client:
            raise RuntimeError("Twilio not configured")

        try:
            call = self.client.calls.create(
                to=request.to_number,
                from_=request.from_number or self.phone_number,
                url=request.webhook_url or "https://demo.twilio.com/welcome/voice/",
                status_callback=request.webhook_url,
                status_callback_event=["initiated", "ringing", "answered", "completed"],
            )
            return CallResult(
                call_sid=call.sid,
                status=call.status,
                direction="outbound",
                from_number=request.from_number or self.phone_number,
                to_number=request.to_number,
            )
        except Exception as e:
            logger.error("twilio.make_call_failed", error=str(e))
            return CallResult(call_sid="", status="failed", direction="outbound", error=str(e))

    async def end_call(self, call_sid: str) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Twilio not configured"}
        try:
            call = self.client.calls(call_sid).update(status="completed")
            return {"call_sid": call.sid, "status": call.status}
        except Exception as e:
            logger.error("twilio.end_call_failed", error=str(e))
            return {"error": str(e)}

    async def get_call_status(self, call_sid: str) -> Dict[str, Any]:
        if not self.client:
            return {"error": "Twilio not configured"}
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                "call_sid": call.sid,
                "status": call.status,
                "duration": call.duration,
                "from": call.from_,
                "to": call.to,
            }
        except Exception as e:
            logger.error("twilio.get_status_failed", error=str(e))
            return {"error": str(e)}

    async def handle_webhook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate TwiML for incoming call handling."""
        response = VoiceResponse()

        # Connect to LiveKit WebSocket stream
        connect = Connect()
        stream_url = payload.get("stream_url", "wss://livekit.dummy")
        connect.stream(url=stream_url)
        response.append(connect)

        return {
            "twiml": str(response),
            "content_type": "application/xml",
        }

    async def healthcheck(self) -> Dict[str, Any]:
        if not self.client:
            return {"status": "down", "error": "Twilio credentials not configured"}
        try:
            account = self.client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()
            return {
                "status": "healthy",
                "account_status": account.status,
                "friendly_name": account.friendly_name,
            }
        except Exception as e:
            return {"status": "down", "error": str(e)}
