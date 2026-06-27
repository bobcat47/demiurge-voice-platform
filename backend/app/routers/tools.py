"""
Tool API Routes

Manage the tool registry.
"""

from typing import List, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import Tool
from app.schemas import ToolCreate, ToolUpdate, ToolResponse
from app.tools.registry import get_tool_registry
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/tools", tags=["Tools"])


@router.get("", response_model=List[ToolResponse])
async def list_tools(
    db: AsyncSession = Depends(get_db),
    enabled_only: bool = Query(True),
    limit: int = Query(100, ge=1, le=1000),
):
    """List all registered tools (built-in + custom)."""
    query = select(Tool).order_by(desc(Tool.created_at))
    if enabled_only:
        query = query.where(Tool.enabled == True)
    query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ToolResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    data: ToolCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new tool."""
    tool = Tool(**data.model_dump())
    db.add(tool)
    await db.commit()
    await db.refresh(tool)
    return tool


@router.get("/builtin")
async def list_builtin_tools():
    """List all built-in Demiurge tools (from registry)."""
    registry = get_tool_registry()
    tools = []
    for tool in registry.list_tools(enabled_only=False):
        tools.append({
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
            "output_schema": tool.output_schema,
            "enabled": tool.enabled,
        })
    return {"tools": tools, "count": len(tools)}


@router.post("/{tool_name}/execute")
async def execute_tool(
    tool_name: str,
    params: Dict[str, Any],
):
    """Execute a tool by name with parameters."""
    registry = get_tool_registry()
    result = await registry.execute(tool_name, params)
    return result


@router.get("/{tool_id}", response_model=ToolResponse)
async def get_tool(
    tool_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a tool by ID."""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
    return tool


@router.put("/{tool_id}", response_model=ToolResponse)
async def update_tool(
    tool_id: UUID,
    data: ToolUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a tool."""
    result = await db.execute(select(Tool).where(Tool.id == tool_id))
    tool = result.scalar_one_or_none()
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(tool, field, value)
    await db.commit()
    await db.refresh(tool)
    return tool
