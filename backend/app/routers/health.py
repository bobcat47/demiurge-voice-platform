"""
Health check endpoint.
"""

from datetime import datetime, timezone
from fastapi import APIRouter

from app.config import settings
from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Platform health check for Railway, load balancers, etc."""
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        environment=settings.ENV,
        timestamp=datetime.now(timezone.utc),
        services={"database": "ok", "api": "ok"},
    )
