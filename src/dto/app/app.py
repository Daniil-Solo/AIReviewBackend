from pydantic import Field

from src.dto.common import BaseDTO


class AppSettingsResponseDTO(BaseDTO):
    email_confirmation_enabled: bool = Field(description="Включено ли подтверждение email при регистрации")
