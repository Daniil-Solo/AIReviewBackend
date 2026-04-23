import datetime

from pydantic import Field

from src.dto.common import BaseDTO


class TaskCreateDTO(BaseDTO):
    workspace_id: int = Field(description="Идентификатор рабочего пространства")
    name: str = Field(min_length=1, max_length=255, description="Название задачи")
    description: str = Field(default="", max_length=5000, description="Описание задачи")


class TaskUpdateDTO(BaseDTO):
    name: str = Field(min_length=1, max_length=255, description="Название задачи")
    description: str = Field(default="", max_length=5000, description="Описание задачи")
    is_active: bool = Field(description="Флаг активности задачи")


class TaskResponseDTO(BaseDTO):
    id: int = Field(description="ID задачи")
    workspace_id: int = Field(description="Идентификатор рабочего пространства")
    name: str = Field(description="Название задачи")
    description: str = Field(description="Описание задачи")
    is_active: bool = Field(description="Флаг активности задачи")
    created_by: int = Field(description="ID пользователя, создавшего задачу")
    created_at: datetime.datetime = Field(description="Дата создания")
    use_exam: bool = Field(description="Флаг использования экзамена")


class TaskFiltersDTO(BaseDTO):
    workspace_id: int | None = Field(default=None, description="Идентификатор рабочего пространства")
    is_active: bool | None = Field(default=None, description="Фильтр по активности")
    ids: list[int] | None = Field(default=None, description="Фильтр по ID задач")


class TaskPublicResponseDTO(BaseDTO):
    id: int = Field(description="ID задачи")
    name: str = Field(description="Название задачи")
    description: str = Field(description="Описание задачи")
