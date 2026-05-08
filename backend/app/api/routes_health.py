"""Health check endpoints."""

from fastapi import APIRouter

from app.core.config import get_settings
from app.models.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        github_available=settings.github_available,
        llm_available=settings.llm_available,
        embedding_model=settings.embedding_model,
    )
