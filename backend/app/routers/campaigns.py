"""
Campaign API Routes

Manage outbound call campaigns.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.models import Campaign
from app.schemas import CampaignCreate, CampaignUpdate, CampaignResponse
from app.core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/v1/campaigns", tags=["Campaigns"])


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = Query(None),
    agent_id: Optional[UUID] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """List all campaigns."""
    query = select(Campaign).order_by(desc(Campaign.created_at))
    if status:
        query = query.where(Campaign.status == status)
    if agent_id:
        query = query.where(Campaign.agent_id == agent_id)
    query = query.limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    data: CampaignCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new outbound campaign."""
    campaign = Campaign(**data.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    logger.info("campaign.created", campaign_id=str(campaign.id), name=campaign.name)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get a campaign by ID."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    data: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update a campaign."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/start")
async def start_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Start a campaign (change status to running)."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found")
    campaign.status = "running"
    await db.commit()
    logger.info("campaign.started", campaign_id=str(campaign.id))
    return {"campaign_id": str(campaign.id), "status": "running"}


@router.post("/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """Pause a running campaign."""
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign '{campaign_id}' not found")
    campaign.status = "paused"
    await db.commit()
    return {"campaign_id": str(campaign.id), "status": "paused"}
