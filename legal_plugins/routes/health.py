"""Health check route."""
from fastapi import APIRouter

from legal_plugins.config import settings
from legal_plugins.skill_registry import registry

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.VERSION,
        "skill_count": registry.count(),
    }
