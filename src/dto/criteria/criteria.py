import datetime

from pydantic import Field

from src.constants.ai_review import CriterionStageEnum
from src.dto.common import BaseDTO


class CriterionCreateDTO(BaseDTO):
    description: str = Field(min_length=1, max_length=1000, description="Описание критерия")
    tags: list[str] = Field(default_factory=list, description="Теги критерия")
    stage: CriterionStageEnum | None = Field(default=None, description="Стадия проверки критерия")
    is_public: bool = Field(default=True, description="Флаг публичности критерия")


class CriterionUpdateDTO(CriterionCreateDTO):
    pass


class CriterionResponseDTO(BaseDTO):
    id: int = Field(description="Идентификатор критерия")
    description: str = Field(description="Описание критерия")
    tags: list[str] = Field(description="Теги критерия")
    stage: CriterionStageEnum | None = Field(description="Стадия проверки критерия")
    is_public: bool = Field(description="Флаг публичности критерия")
    created_by: int = Field(description="ID пользователя-автора критерия")
    created_at: datetime.datetime = Field(description="Дата создания")


class CriterionFiltersDTO(BaseDTO):
    search: str | None = Field(default=None, description="Поисковой запрос")
    tags: list[str] | None = Field(default=None, description="Теги")
