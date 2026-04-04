from fastapi import APIRouter

from src.application.health import health as health_service


router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, bool]:
    return await health_service.check()
