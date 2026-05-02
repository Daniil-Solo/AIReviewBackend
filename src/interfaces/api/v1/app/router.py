from fastapi import APIRouter

from src.constants.emails import EmailSenderTypeEnum
from src.dto.app.app import AppSettingsResponseDTO
from src.settings import settings


router = APIRouter(prefix="/app", tags=["app"])


@router.get("/settings", response_model=AppSettingsResponseDTO)
async def get_app_settings() -> AppSettingsResponseDTO:
    return AppSettingsResponseDTO(email_confirmation_enabled=settings.email.TYPE != EmailSenderTypeEnum.DISABLE)
