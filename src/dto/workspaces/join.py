from pydantic import Field

from src.dto.common import BaseDTO


class JoinBySlugDTO(BaseDTO):
    slug: str = Field(description="Slug приглашения")
    password: str | None = Field(default=None, description="Пароль для вступления")


class JoinResponseDTO(BaseDTO):
    workspace_id: int = Field(description="ID рабочего пространства")


class SlugCheckResponseDTO(BaseDTO):
    slug: str = Field(description="Slug приглашения")
    is_available: bool = Field(description="Доступен ли slug")
