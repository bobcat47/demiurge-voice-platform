"""
Call API Routes

Manage voice calls and their lifecycle.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import Call
from app.schemas import (
    CallCreate, CallUpdate, CallResponse,
    PipelineConfig, PipelineStartResponse,
    CallSummaryRequest, CallSummaryResponse,
)
from app.services.voice_pipeline import VoicePipelineService
from app.services.call_summary import CallSummaryService
from app.services.call_session_manager import CallSessionManager
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/calls", tags=["Calls"])

# Shared services
_pipeline_service: Optional[VoicePipelineService] = None
_session_manager: Optional[CallSessionManager] = None


def get_pipeline_service():
    global _pipeline_service
    if _pipeline_service is None:
        _pipeline_service = VoicePipelineService()
    return _pipeline_service


def get_session_manager():
    global _session_manager
    if _session_manager is None:
        _session_manager = CallSessionManager()
    return _session_manager


@router.get("", response_model=List[CallResponse])
async def list_calls(
    db: AsyncSession = Depends(get_db),
    agent_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    direction: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List all calls with optional filters."""
    query = select(Call).order_by(desc(Call.created_at))
    if agent_id:
        query = query.where(Call.agent_id == agent_id)
    if status:
        query = query.where(Call.status == status)
    if direction:
        query = query.where(Call.direction == direction)
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=CallResponse, status_code=status.HTTP_201_CREATED)
async def create_call(
    data: CallCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new call record."""
    call = Call(**data.model_dump())
    db.add(call)
    await db.commit()
    await db.refresh(call)
    logger.info("call.created", call_id=str(call.id), agent_id=str(call.agent_id))
    return call


@router.get("/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a single call by ID."""
    result = await db.execute(select(Call).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail=f"Call '{call_id}' not found")
    return call


@router.put("/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: UUID,
    data: CallUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a call record."""
    result = await db.execute(select(Call).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail=f"Call '{call_id}' not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(call, field, value)

    await db.commit()
    await db.refresh(call)
    return call


@router.post("/{call_id}/start", response_model=PipelineStartResponse)
async def start_call_pipeline(
    call_id: UUID,
    config: PipelineConfig,
    db: AsyncSession = Depends(get_db),
):
    """Start the voice pipeline for a call."""
    pipeline = get_pipeline_service()

    # Get agent config
    from app.models import Agent
    result = await db.execute(select(Agent).where(Agent.id == config.agent_id))
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{config.agent_id}' not found")

    agent_config = {
        "system_prompt": agent.system_prompt,
        "llm_provider": agent.llm_provider,
        "llm_model": agent.llm_model,
        "voice_provider": agent.voice_provider,
        "voice_id": agent.voice_id,
        "stt_provider": agent.stt_provider,
        "tts_provider": agent.tts_provider,
        "tools_enabled": agent.tools_enabled,
        "memory_enabled": agent.memory_enabled,
    }

    result = await pipeline.start_call(
        agent_id=str(config.agent_id),
        agent_config=agent_config,
        phone_number=config.phone_number,
        direction=config.direction,
    )

    # Update call record
    call_result = await db.execute(select(Call).where(Call.id == call_id))
    call = call_result.scalar_one_or_none()
    if call:
        call.status = "in_progress"
        call.started_at = datetime.now(timezone.utc)
        await db.commit()

    return PipelineStartResponse(
        call_id=UUID(result["call_id"]),
        status=result["status"],
        message="Voice pipeline started",
        ws_url=result.get("ws_url"),
    )


@router.post("/{call_id}/end")
async def end_call_pipeline(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """End a voice call pipeline."""
    pipeline = get_pipeline_service()
    result = await pipeline.end_call(str(call_id))

    # Update call record
    call_result = await db.execute(select(Call).where(Call.id == call_id))
    call = call_result.scalar_one_or_none()
    if call:
        call.status = "completed"
        call.ended_at = datetime.now(timezone.utc)
        if call.started_at:
            call.duration_seconds = int((call.ended_at - call.started_at).total_seconds())
        await db.commit()

    return result


@router.post("/{call_id}/text-turn")
async def text_turn(
    call_id: UUID,
    request: dict,
    db: AsyncSession = Depends(get_db),
):
    """Process a text turn for a call (testing / text-based agents)."""
    pipeline = get_pipeline_service()
    user_text = request.get("text", "")
    result = await pipeline.process_text_turn(str(call_id), user_text)
    return result


@router.post("/{call_id}/summarize", response_model=CallSummaryResponse)
async def summarize_call(
    call_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Generate a summary of a call transcript."""
    result = await db.execute(select(Call).where(Call.id == call_id))
    call = result.scalar_one_or_none()
    if not call:
        raise HTTPException(status_code=404, detail=f"Call '{call_id}' not found")

    summary_service = CallSummaryService()
    summary = await summary_service.summarize(call.transcript or "")

    # Save summary
    call.summary = summary["summary"]
    await db.commit()

    return CallSummaryResponse(**summary)
