"""
Memory API Routes

Per-agent conversation memory management.
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import Memory
from app.schemas import MemoryCreate, MemoryResponse
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/memory", tags=["Memory"])


@router.get("/{agent_id}", response_model=List[MemoryResponse])
async def get_memory(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
    call_id: UUID = Query(None),
):
    """Get conversation memory for an agent."""
    query = (
        select(Memory)
        .where(Memory.agent_id == agent_id)
        .order_by(desc(Memory.created_at))
        .limit(limit)
    )
    if call_id:
        query = query.where(Memory.call_id == call_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{agent_id}", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
async def add_memory(
    agent_id: UUID,
    data: MemoryCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a memory entry for an agent."""
    entry = Memory(
        agent_id=agent_id,
        call_id=data.call_id,
        role=data.role,
        content=data.content,
        tool_calls=data.tool_calls,
        tool_results=data.tool_results,
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def clear_memory(
    agent_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Clear all memory for an agent."""
    from sqlalchemy import delete
    await db.execute(delete(Memory).where(Memory.agent_id == agent_id))
    await db.commit()
    return None
