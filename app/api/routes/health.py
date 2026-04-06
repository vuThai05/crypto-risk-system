"""Health check endpoint."""

from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check() -> dict:
    """Liveness probe — returns OK when the API is running."""
    return {"status": "ok"}
