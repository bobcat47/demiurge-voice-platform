"""
Provider API Routes

Query and manage AI providers (LLM, STT, TTS, telephony).
"""

from fastapi import APIRouter
from typing import Dict, Any

from app.providers.llm.factory import list_available_providers as list_llm_providers
from app.providers.stt.factory import get_stt_provider
from app.providers.tts.factory import get_tts_provider
from app.providers.telephony.factory import get_telephony_provider
from app.providers.livekit.adapter import LiveKitAdapter
from app.providers.pipecat.adapter import PipecatAdapter
from app.config import settings

router = APIRouter(prefix="/api/v1/providers", tags=["Providers"])


@router.get("")
async def list_providers():
    """List all configured providers and their status."""
    return {
        "llm": {
            "active": settings.LLM_PROVIDER,
            "model": settings.LLM_MODEL,
            "available": list_llm_providers(),
        },
        "stt": {
            "active": settings.STT_PROVIDER,
            "model": settings.STT_MODEL,
        },
        "tts": {
            "active": settings.TTS_PROVIDER,
            "voice": settings.TTS_VOICE,
        },
        "telephony": {
            "active": settings.TELEPHONY_PROVIDER,
        },
        "livekit": {
            "configured": bool(settings.LIVEKIT_URL and settings.LIVEKIT_API_KEY),
            "url": settings.LIVEKIT_URL,
        },
        "pipecat": {
            "configured": bool(settings.PIPECAT_DAILY_API_KEY),
        },
    }


@router.get("/health")
async def providers_health():
    """Health check all providers."""
    results = {}

    # LLM
    try:
        from app.providers.llm.factory import get_llm_provider
        llm = get_llm_provider()
        results["llm"] = await llm.healthcheck()
    except Exception as e:
        results["llm"] = {"status": "error", "error": str(e)}

    # STT
    try:
        stt = get_stt_provider()
        results["stt"] = await stt.healthcheck()
    except Exception as e:
        results["stt"] = {"status": "error", "error": str(e)}

    # TTS
    try:
        tts = get_tts_provider()
        results["tts"] = await tts.healthcheck()
    except Exception as e:
        results["tts"] = {"status": "error", "error": str(e)}

    # Telephony
    try:
        telephony = get_telephony_provider()
        results["telephony"] = await telephony.healthcheck()
    except Exception as e:
        results["telephony"] = {"status": "error", "error": str(e)}

    # LiveKit
    lk = LiveKitAdapter()
    results["livekit"] = await lk.healthcheck()

    # Pipecat
    pc = PipecatAdapter()
    results["pipecat"] = await pc.healthcheck()

    return results
