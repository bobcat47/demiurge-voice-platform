"""
Analytics API Routes

Dashboard data and summary statistics.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from app.database import get_db
from app.models import Call, Agent, AnalyticsDaily
from app.schemas import AnalyticsSummary, CallResponse
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    agent_id: Optional[UUID] = Query(None),
):
    """Get analytics summary for the dashboard."""

    # Total calls
    call_query = select(func.count(Call.id))
    if agent_id:
        call_query = call_query.where(Call.agent_id == agent_id)
    result = await db.execute(call_query)
    total_calls = result.scalar() or 0

    # Total agents
    agents_result = await db.execute(select(func.count(Agent.id)).where(Agent.active == True))
    total_agents = agents_result.scalar() or 0

    # Average duration
    avg_query = select(func.avg(Call.duration_seconds))
    if agent_id:
        avg_query = avg_query.where(Call.agent_id == agent_id)
    avg_result = await db.execute(avg_query)
    avg_duration = float(avg_result.scalar() or 0)

    # Today's calls
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_query = select(func.count(Call.id)).where(Call.created_at >= today_start)
    if agent_id:
        today_query = today_query.where(Call.agent_id == agent_id)
    today_result = await db.execute(today_query)
    calls_today = today_result.scalar() or 0

    # This week's calls
    week_start = today_start - timedelta(days=today_start.weekday())
    week_query = select(func.count(Call.id)).where(Call.created_at >= week_start)
    if agent_id:
        week_query = week_query.where(Call.agent_id == agent_id)
    week_result = await db.execute(week_query)
    calls_this_week = week_result.scalar() or 0

    # Recent calls
    recent_query = (
        select(Call)
        .order_by(desc(Call.created_at))
        .limit(10)
    )
    if agent_id:
        recent_query = recent_query.where(Call.agent_id == agent_id)
    recent_result = await db.execute(recent_query)
    recent_calls = recent_result.scalars().all()

    # Provider health (placeholder)
    provider_health = {
        "llm": "healthy",
        "stt": "healthy",
        "tts": "healthy",
        "telephony": "healthy",
    }

    return AnalyticsSummary(
        total_calls=total_calls,
        total_agents=total_agents,
        avg_duration_seconds=avg_duration,
        calls_today=calls_today,
        calls_this_week=calls_this_week,
        provider_health=provider_health,
        recent_calls=recent_calls,
    )


@router.get("/recordings")
async def list_recordings(
    db: AsyncSession = Depends(get_db),
    agent_id: Optional[UUID] = Query(None),
    limit: int = Query(50, ge=1, le=500),
):
    """List calls with recordings."""
    query = (
        select(Call)
        .where(Call.recording_url.isnot(None))
        .order_by(desc(Call.created_at))
        .limit(limit)
    )
    if agent_id:
        query = query.where(Call.agent_id == agent_id)
    result = await db.execute(query)
    return result.scalars().all()
