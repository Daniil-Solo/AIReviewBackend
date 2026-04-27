import datetime

from pydantic import Field, computed_field, field_validator

from src.constants.ai_review import CriterionStageEnum
from src.dto.common import BaseDTO


class CriterionCreateDTO(BaseDTO):
    description: str = Field(min_length=1, max_length=1000, description="Описание критерия")
    tags: list[str] = Field(default_factory=list, description="Теги критерия")
    stage: CriterionStageEnum | None = Field(default=None, description="Стадия проверки критерия")
    prompt: str = Field(description="Промпт для AI-проверки критерия")
    workspace_id: int | None = Field(default=None, description="ID workspace для workspace-level критерия")
    task_id: int | None = Field(default=None, description="ID задачи для task-level критерия")

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v):
        if isinstance(v, list):
            return [tag.lower() for tag in v]
        return v


class CriterionUpdateDTO(CriterionCreateDTO):
    pass


class CriterionResponseDTO(BaseDTO):
    id: int = Field(description="Идентификатор критерия")
    description: str = Field(description="Описание критерия")
    prompt: str = Field(description="Промпт для AI-проверки критерия")
    tags: list[str] = Field(description="Теги критерия")
    stage: CriterionStageEnum | None = Field(description="Стадия проверки критерия")
    workspace_id: int | None = Field(description="ID workspace для workspace-level критерия")
    task_id: int | None = Field(description="ID задачи для task-level критерия")
    created_by: int = Field(description="ID пользователя-автора критерия")
    created_at: datetime.datetime = Field(description="Дата создания")

    @computed_field
    def is_public(self) -> bool:
        return self.workspace_id is None and self.task_id is None


class CriterionFiltersDTO(BaseDTO):
    search: str | None = Field(default=None, description="Поисковой запрос")
    tags: list[str] | None = Field(default=None, description="Теги")
    workspace_id: int | None = Field(default=None, description="ID workspace для workspace-level критерия")
    task_id: int | None = Field(default=None, description="ID задачи для task-level критерия")

    @field_validator("tags", mode="before")
    @classmethod
    def normalize_tags(cls, v):
        if isinstance(v, list):
            return [tag.lower() for tag in v]
        return v
