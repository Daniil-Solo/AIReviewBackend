from fastapi import APIRouter, HTTPException

from src.infrastructure.database import check_database_connection


router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    try:
        await check_database_connection()
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail={"status": "error", "db": "disconnected"}) from e
