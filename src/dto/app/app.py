from src.dto.common import BaseDTO
from pydantic import Field


class AppSettingsResponseDTO(BaseDTO):
    email_confirmation_enabled: bool = Field(description="Включено ли подтверждение email при регистрации")
