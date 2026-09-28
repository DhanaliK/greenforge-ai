"""Health check endpoint."""
from fastapi import APIRouter
from app.core.config import settings
from app.providers.ai_provider import get_ai_provider

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health():
    provider = get_ai_provider()
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ai_provider": provider.name,
        "ai_provider_available": provider.is_available,
        "demo_mode": not provider.is_available,
    }
