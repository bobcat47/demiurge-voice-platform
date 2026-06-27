"""
Voice API Routes

Manage voice presets / TTS voices.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import Voice
from app.schemas import VoiceCreate, VoiceUpdate, VoiceResponse
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/voices", tags=["Voices"])


@router.get("", response_model=List[VoiceResponse])
async def list_voices(
    db: AsyncSession = Depends(get_db),
    provider: str = Query(None),
    language: str = Query(None),
    enabled_only: bool = Query(True),
    limit: int = Query(100, ge=1, le=1000),
):
    """List available TTS voices."""
    query = select(Voice).order_by(desc(Voice.created_at))
    if provider:
        query = query.where(Voice.provider == provider)
    if language:
        query = query.where(Voice.language == language)
    if enabled_only:
        query = query.where(Voice.enabled == True)
    query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=VoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_voice(
    data: VoiceCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a new voice preset."""
    voice = Voice(**data.model_dump())
    db.add(voice)
    await db.commit()
    await db.refresh(voice)
    return voice


@router.get("/{voice_id}", response_model=VoiceResponse)
async def get_voice(
    voice_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a voice preset by ID."""
    result = await db.execute(select(Voice).where(Voice.id == voice_id))
    voice = result.scalar_one_or_none()
    if not voice:
        raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")
    return voice


@router.put("/{voice_id}", response_model=VoiceResponse)
async def update_voice(
    voice_id: UUID,
    data: VoiceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a voice preset."""
    result = await db.execute(select(Voice).where(Voice.id == voice_id))
    voice = result.scalar_one_or_none()
    if not voice:
        raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(voice, field, value)
    await db.commit()
    await db.refresh(voice)
    return voice
