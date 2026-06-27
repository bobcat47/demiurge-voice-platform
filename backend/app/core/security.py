"""
Demiurge Voice Platform — Security Utilities

API key validation for admin endpoints.
"""

from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
admin_key_header = APIKeyHeader(name="X-Admin-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify a standard API key if ADMIN_API_KEY is configured."""
    if not settings.ADMIN_API_KEY:
        return "unsecured"
    if api_key == settings.ADMIN_API_KEY:
        return api_key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API key.",
    )


async def verify_admin_key(admin_key: str = Security(admin_key_header)) -> str:
    """Verify admin access for sensitive endpoints."""
    if not settings.ADMIN_API_KEY:
        return "unsecured"
    if admin_key == settings.ADMIN_API_KEY:
        return admin_key
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required.",
    )
